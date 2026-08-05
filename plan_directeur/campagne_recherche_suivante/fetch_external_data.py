#!/usr/bin/env python3
"""Acquiert, contrôle et inventorie les données externes des nouveaux tests.

Principes appliqués :

- résolution des fichiers Dryad depuis le DOI et la version publique courante ;
- conservation exacte du chemin lors des redirections vers des URL signées ;
- repli vers l'archive complète lorsque les téléchargements individuels échouent ;
- téléchargement dans une zone temporaire, puis remplacement atomique du cache ;
- validation du type réel des fichiers avant qu'ils soient utilisés par les tests ;
- conservation d'un cache complet antérieur si un rafraîchissement réseau échoue.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import shutil
import ssl
import stat
import time
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(__file__).with_name("sources_externes.json")
DEST = ROOT / "donnees_externes"

REDIRECT_STATUSES = {301, 302, 303, 307, 308}
RETRYABLE_STATUSES = {403, 408, 409, 425, 429, 500, 502, 503, 504}
DEFAULT_HEADERS = {
    "User-Agent": "ORI-C scientific-research acquisition/2.1",
    "Accept": "*/*",
    "Accept-Encoding": "identity",
}
DRYAD_ORIGIN = "https://datadryad.org"


class AcquisitionError(RuntimeError):
    """Erreur d'acquisition avec contexte exploitable dans le rapport JSON."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status: int | None = None,
        details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.url = url
        self.status = status
        self.details = details

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {"error": str(self)}
        if self.url:
            result["url"] = self.url
        if self.status is not None:
            result["http_status"] = self.status
        if self.details:
            result["details"] = self.details
        return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def combined_sha256(files: list[dict[str, object]]) -> str:
    """Empreinte déterministe d'un jeu composé de plusieurs fichiers."""
    digest = hashlib.sha256()
    for item in sorted(files, key=lambda value: str(value["name"])):
        digest.update(str(item["name"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["sha256"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _connection(url: str, timeout: int) -> tuple[http.client.HTTPConnection, str]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise AcquisitionError("URL HTTP(S) invalide", url=url)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    if parsed.scheme == "https":
        context = ssl.create_default_context()
        connection: http.client.HTTPConnection = http.client.HTTPSConnection(
            parsed.hostname,
            parsed.port or 443,
            timeout=timeout,
            context=context,
        )
    else:
        connection = http.client.HTTPConnection(
            parsed.hostname,
            parsed.port or 80,
            timeout=timeout,
        )
    return connection, path


def _body_excerpt(response: http.client.HTTPResponse, limit: int = 2048) -> str:
    try:
        data = response.read(limit)
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace").strip()


def _follow_request(
    url: str,
    *,
    timeout: int,
    max_redirects: int = 12,
    headers: dict[str, str] | None = None,
) -> tuple[http.client.HTTPConnection, http.client.HTTPResponse, str, list[str]]:
    """Suit les redirections sans réencoder le chemin de l'URL courante."""
    current = url
    redirects: list[str] = []
    request_headers = {**DEFAULT_HEADERS, **(headers or {})}

    for _ in range(max_redirects + 1):
        connection, request_target = _connection(current, timeout)
        try:
            connection.request("GET", request_target, headers=request_headers)
            response = connection.getresponse()
        except Exception:
            connection.close()
            raise

        if response.status not in REDIRECT_STATUSES:
            return connection, response, current, redirects

        location = response.getheader("Location")
        response.read()
        connection.close()
        if not location:
            raise AcquisitionError(
                "redirection HTTP sans en-tête Location",
                url=current,
                status=response.status,
            )
        next_url = urljoin(current, location)
        previous_parts = urlsplit(current)
        next_parts = urlsplit(next_url)
        previous_origin = (
            previous_parts.scheme.lower(),
            previous_parts.hostname,
            previous_parts.port,
        )
        next_origin = (
            next_parts.scheme.lower(),
            next_parts.hostname,
            next_parts.port,
        )
        if previous_origin != next_origin:
            # Ne jamais transmettre les secrets Dryad ni les cookies de session
            # au stockage objet visé par une redirection présignée.
            request_headers.pop("Authorization", None)
            request_headers.pop("Cookie", None)
        current = next_url
        redirects.append(current)

    raise AcquisitionError(
        f"trop de redirections HTTP, maximum {max_redirects}",
        url=current,
    )


def fetch_bytes(
    url: str,
    *,
    timeout: int = 120,
    max_bytes: int = 16 * 1024 * 1024,
) -> tuple[bytes, dict[str, object]]:
    connection: http.client.HTTPConnection | None = None
    try:
        connection, response, final_url, redirects = _follow_request(url, timeout=timeout)
        if not 200 <= response.status < 300:
            excerpt = _body_excerpt(response)
            raise AcquisitionError(
                f"HTTP {response.status} pendant la lecture des métadonnées",
                url=final_url,
                status=response.status,
                details=excerpt,
            )
        content_length = response.getheader("Content-Length")
        if content_length and int(content_length) > max_bytes:
            raise AcquisitionError(
                f"réponse de métadonnées trop volumineuse: {content_length} octets",
                url=final_url,
            )
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise AcquisitionError(
                f"réponse de métadonnées supérieure à {max_bytes} octets",
                url=final_url,
            )
        receipt = {
            "requested_url": url,
            "final_url": final_url,
            "http_status": response.status,
            "content_type": response.getheader("Content-Type"),
            "etag": response.getheader("ETag"),
            "last_modified": response.getheader("Last-Modified"),
            "redirects": redirects,
        }
        return data, receipt
    except AcquisitionError:
        raise
    except Exception as exc:
        raise AcquisitionError(
            f"échec de lecture HTTP: {type(exc).__name__}: {exc}",
            url=url,
        ) from exc
    finally:
        if connection is not None:
            connection.close()


def fetch_json(url: str, *, timeout: int = 120) -> tuple[dict[str, object], dict[str, object]]:
    data, receipt = fetch_bytes(url, timeout=timeout)
    try:
        document = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AcquisitionError(
            f"réponse JSON invalide: {exc}",
            url=str(receipt.get("final_url") or url),
        ) from exc
    if not isinstance(document, dict):
        raise AcquisitionError("la réponse JSON racine n'est pas un objet", url=url)
    return document, receipt


def download_once(
    url: str,
    temporary: Path,
    *,
    timeout: int,
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    connection: http.client.HTTPConnection | None = None
    try:
        connection, response, final_url, redirects = _follow_request(
            url, timeout=timeout, headers=headers
        )
        if not 200 <= response.status < 300:
            excerpt = _body_excerpt(response)
            raise AcquisitionError(
                f"HTTP {response.status} pendant le téléchargement",
                url=final_url,
                status=response.status,
                details=excerpt,
            )

        digest = hashlib.sha256()
        size = 0
        with temporary.open("wb") as destination:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                destination.write(block)
                digest.update(block)
                size += len(block)
        if size == 0:
            raise AcquisitionError("réponse de téléchargement vide", url=final_url)
        return {
            "requested_url": url,
            "final_url": final_url,
            "http_status": response.status,
            "content_type": response.getheader("Content-Type"),
            "etag": response.getheader("ETag"),
            "last_modified": response.getheader("Last-Modified"),
            "redirects": redirects,
            "sha256": digest.hexdigest(),
            "size_bytes": size,
        }
    except AcquisitionError:
        raise
    except Exception as exc:
        raise AcquisitionError(
            f"échec de téléchargement: {type(exc).__name__}: {exc}",
            url=url,
        ) from exc
    finally:
        if connection is not None:
            connection.close()


def download(
    url: str,
    target: Path,
    *,
    retries: int = 4,
    timeout: int = 300,
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    """Télécharge atomiquement un fichier et retourne sa provenance HTTP."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.part")
    last_error: AcquisitionError | None = None

    for attempt in range(1, retries + 1):
        temporary.unlink(missing_ok=True)
        try:
            receipt = download_once(url, temporary, timeout=timeout, headers=headers)
            temporary.replace(target)
            receipt["attempts"] = attempt
            return receipt
        except AcquisitionError as exc:
            last_error = exc
            temporary.unlink(missing_ok=True)
            retryable = exc.status is None or exc.status in RETRYABLE_STATUSES
            if attempt >= retries or not retryable:
                break
            time.sleep(min(2**attempt, 16))

    assert last_error is not None
    raise AcquisitionError(
        f"échec après {retries} tentative(s): {last_error}",
        url=last_error.url or url,
        status=last_error.status,
        details=last_error.details,
    ) from last_error



def _oauth_token_request(client_id: str, client_secret: str, *, timeout: int) -> str:
    """Obtient un jeton Dryad par le flux officiel client_credentials."""
    payload = json.dumps(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    connection, target = _connection(f"{DRYAD_ORIGIN}/oauth/token", timeout)
    try:
        connection.request(
            "POST",
            target,
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": DEFAULT_HEADERS["User-Agent"],
            },
        )
        response = connection.getresponse()
        body = response.read(1024 * 1024)
        if not 200 <= response.status < 300:
            raise AcquisitionError(
                f"HTTP {response.status} pendant l'authentification Dryad",
                url=f"{DRYAD_ORIGIN}/oauth/token",
                status=response.status,
                details=body.decode("utf-8", errors="replace")[:2048],
            )
        document = json.loads(body.decode("utf-8"))
        token = document.get("access_token")
        if not isinstance(token, str) or not token:
            raise AcquisitionError("réponse OAuth Dryad sans access_token")
        return token
    finally:
        connection.close()


def dryad_auth_headers(*, timeout: int) -> tuple[dict[str, str] | None, str]:
    """Retourne les en-têtes officiels Dryad ou signale l'absence de secrets.

    Variables reconnues :
    - DRYAD_API_TOKEN, pour un jeton déjà émis ;
    - DRYAD_API_CLIENT_ID et DRYAD_API_CLIENT_SECRET, pour renouveler le jeton.
    """
    token = os.environ.get("DRYAD_API_TOKEN", "").strip()
    if token:
        return {"Authorization": f"Bearer {token}", "Accept": "*/*"}, "bearer_token"

    client_id = os.environ.get("DRYAD_API_CLIENT_ID", "").strip()
    client_secret = os.environ.get("DRYAD_API_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        token = _oauth_token_request(client_id, client_secret, timeout=timeout)
        return {"Authorization": f"Bearer {token}", "Accept": "*/*"}, "client_credentials"
    return None, "none"


def validate_payload(path: Path, expected_name: str | None = None) -> None:
    """Écarte les réponses HTML/XML et vérifie les formats utilisés par ORI-C."""
    if not path.exists() or path.stat().st_size == 0:
        raise AcquisitionError(f"fichier absent ou vide: {path.name}")

    name = expected_name or path.name
    suffix = Path(name).suffix.lower()
    head = path.read_bytes()[:4096].lstrip().lower()
    if head.startswith((b"<!doctype html", b"<html", b"<?xml")):
        excerpt = head[:300].decode("utf-8", errors="replace")
        raise AcquisitionError(
            f"le téléchargement de {name} contient une page HTML/XML au lieu des données",
            details=excerpt,
        )

    if suffix == ".xlsx":
        if not zipfile.is_zipfile(path):
            raise AcquisitionError(f"{name} n'est pas un classeur XLSX valide")
        with zipfile.ZipFile(path) as archive:
            members = set(archive.namelist())
            required = {"[Content_Types].xml", "xl/workbook.xml"}
            if not required.issubset(members):
                raise AcquisitionError(f"{name} ne contient pas la structure minimale d'un XLSX")
    elif suffix == ".csv":
        sample = path.read_bytes()[:16384]
        try:
            text = sample.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = sample.decode("latin-1")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if not first_line or not any(delimiter in first_line for delimiter in (",", ";", "\t")):
            raise AcquisitionError(f"{name} ne possède pas d'en-tête tabulaire reconnaissable")
    elif suffix == ".zip" and not zipfile.is_zipfile(path):
        raise AcquisitionError(f"{name} n'est pas une archive ZIP valide")


def safe_extract_zip(raw: Path, destination: Path) -> list[str]:
    """Extrait une archive ZIP sans traversée de chemin ni lien symbolique."""
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    with zipfile.ZipFile(raw) as archive:
        for member in archive.infolist():
            normalized = member.filename.replace("\\", "/")
            relative = PurePosixPath(normalized)
            mode = (member.external_attr >> 16) & 0o170000
            if relative.is_absolute() or ".." in relative.parts:
                raise AcquisitionError(f"chemin interdit dans l'archive: {member.filename}")
            if mode == stat.S_IFLNK:
                raise AcquisitionError(f"lien symbolique interdit dans l'archive: {member.filename}")
            if member.is_dir():
                continue
            target = destination.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted.append(target.relative_to(destination).as_posix())
    return sorted(extracted)


def extract(raw: Path, folder: Path) -> list[str]:
    """Compatibilité avec les tests historiques du paquet."""
    extracted_root = folder / "extracted"
    if extracted_root.exists():
        shutil.rmtree(extracted_root)
    extracted_root.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(raw):
        return safe_extract_zip(raw, extracted_root)
    copied = extracted_root / raw.name
    shutil.copy2(raw, copied)
    return [copied.name]


def _link(document: dict[str, object], *names: str) -> str | None:
    links = document.get("_links")
    if not isinstance(links, dict):
        return None
    for name in names:
        value = links.get(name)
        if isinstance(value, dict) and isinstance(value.get("href"), str):
            return str(value["href"])
    return None


def _embedded(document: dict[str, object], *names: str) -> list[dict[str, object]]:
    embedded = document.get("_embedded")
    if not isinstance(embedded, dict):
        return []
    for name in names:
        value = embedded.get(name)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _absolute(base: str, href: str) -> str:
    return urljoin(base, href)


def paginate_json(
    url: str,
    *,
    embedded_names: tuple[str, ...],
    timeout: int,
    max_pages: int = 100,
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    current: str | None = url
    visited: set[str] = set()
    for _ in range(max_pages):
        if current is None or current in visited:
            break
        visited.add(current)
        document, _ = fetch_json(current, timeout=timeout)
        items.extend(_embedded(document, *embedded_names))
        next_href = _link(document, "next")
        current = _absolute(current, next_href) if next_href else None
    if current is not None and current not in visited:
        raise AcquisitionError(f"pagination supérieure à {max_pages} pages", url=current)
    return items


def resolve_dryad_files(
    dataset: dict[str, object],
    *,
    timeout: int,
) -> tuple[dict[str, str], dict[str, object]]:
    """Résout les identifiants de fichiers depuis le DOI public courant."""
    doi = str(dataset["doi"])
    origin = DRYAD_ORIGIN
    encoded = quote(f"doi:{doi}", safe="")
    dataset_url = f"{origin}/api/v2/datasets/{encoded}"
    metadata, dataset_receipt = fetch_json(dataset_url, timeout=timeout)

    versions_href = _link(metadata, "stash:versions") or f"/api/v2/datasets/{encoded}/versions"
    versions_url = _absolute(dataset_url, versions_href)
    separator = "&" if "?" in versions_url else "?"
    versions = paginate_json(
        f"{versions_url}{separator}per_page=100",
        embedded_names=("stash:versions", "versions"),
        timeout=timeout,
    )
    submitted = [
        item
        for item in versions
        if str(item.get("versionStatus", item.get("status", ""))).lower()
        in {"submitted", "published"}
    ]
    candidates = submitted or versions
    if not candidates:
        raise AcquisitionError("aucune version Dryad publique trouvée", url=versions_url)

    def version_key(item: dict[str, object]) -> tuple[int, str]:
        try:
            number = int(item.get("versionNumber", item.get("version", 0)))
        except (TypeError, ValueError):
            number = 0
        return number, str(item.get("publicationDate", item.get("lastModificationDate", "")))

    latest = max(candidates, key=version_key)
    files_href = _link(latest, "stash:files")
    if not files_href:
        version_id = latest.get("id")
        if version_id is None:
            self_href = _link(latest, "self") or ""
            version_id = self_href.rstrip("/").split("/")[-1]
        if not version_id:
            raise AcquisitionError("identifiant de version Dryad introuvable", url=versions_url)
        files_href = f"/api/v2/versions/{version_id}/files"
    files_url = _absolute(versions_url, files_href)
    separator = "&" if "?" in files_url else "?"
    files = paginate_json(
        f"{files_url}{separator}per_page=100",
        embedded_names=("stash:files", "files"),
        timeout=timeout,
    )

    resolved: dict[str, str] = {}
    file_ids: dict[str, str] = {}
    for item in files:
        path = item.get("path")
        if not isinstance(path, str):
            continue
        self_href = _link(item, "self") or ""
        file_id = self_href.rstrip("/").split("/")[-1]
        if not file_id.isdigit():
            continue
        name = Path(path).name
        resolved[name] = f"{origin}/downloads/file_stream/{file_id}"
        file_ids[name] = file_id

    expected = [str(name) for name in dataset.get("expected_files", [])]
    missing = [name for name in expected if name not in resolved]
    if missing:
        raise AcquisitionError(
            "fichiers attendus absents de la version Dryad courante: " + ", ".join(missing),
            url=files_url,
        )

    resolution = {
        "provider": "dryad",
        "dataset_api_url": dataset_url,
        "dataset_api_receipt": dataset_receipt,
        "versions_url": versions_url,
        "files_url": files_url,
        "version_id": latest.get("id"),
        "version_number": latest.get("versionNumber", latest.get("version")),
        "version_status": latest.get("versionStatus", latest.get("status")),
        "publication_date": latest.get("publicationDate"),
        "resolved_file_ids": file_ids,
    }
    return {name: resolved[name] for name in expected}, resolution


def legacy_file_urls(dataset: dict[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in dataset.get("file_downloads", []):
        if isinstance(item, dict) and "name" in item and "url" in item:
            result[str(item["name"])] = str(item["url"])
    return result


def prepare_staging(folder: Path) -> Path:
    staging = folder / ".acquisition-staging"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "extracted").mkdir(parents=True, exist_ok=True)
    return staging


def provenance_record(
    name: str,
    path: Path,
    receipt: dict[str, object] | None = None,
    *,
    local_path: str | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "name": name,
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }
    if local_path:
        record["local_path"] = local_path
    if receipt:
        record.update(receipt)
    return record


def acquire_individual_files(
    dataset: dict[str, object],
    staging: Path,
    *,
    retries: int,
    timeout: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    expected = [str(name) for name in dataset.get("expected_files", [])]
    resolution_error: dict[str, object] | None = None
    try:
        public_urls, resolution = resolve_dryad_files(dataset, timeout=timeout)
        method = "dryad_api_resolved_files"
    except AcquisitionError as exc:
        resolution_error = exc.as_dict()
        public_urls = legacy_file_urls(dataset)
        resolution = {"provider": "dryad", "resolution_fallback": "registry_file_ids"}
        method = "dryad_registry_file_ids"

    missing_urls = [name for name in expected if name not in public_urls]
    if missing_urls:
        raise AcquisitionError(
            "aucune URL individuelle disponible pour: " + ", ".join(missing_urls),
            url=str(dataset.get("landing_page", "")),
            details=json.dumps(resolution_error, ensure_ascii=False) if resolution_error else None,
        )

    auth_headers, auth_mode = dryad_auth_headers(timeout=timeout)
    file_ids = resolution.get("resolved_file_ids", {})
    records: list[dict[str, object]] = []
    extracted_root = staging / "extracted"
    for name in expected:
        target = extracted_root / name
        file_id = str(file_ids.get(name, "")) if isinstance(file_ids, dict) else ""
        if not file_id:
            file_id = public_urls[name].rstrip("/").split("/")[-1]

        receipt: dict[str, object]
        if auth_headers and file_id.isdigit():
            api_url = f"{DRYAD_ORIGIN}/api/v2/files/{file_id}/download"
            receipt = download(
                api_url,
                target,
                retries=retries,
                timeout=timeout,
                headers=auth_headers,
            )
            receipt["transport"] = "authenticated_api"
        else:
            receipt = download(
                public_urls[name],
                target,
                retries=retries,
                timeout=timeout,
            )
            receipt["transport"] = "public_file_stream"
        validate_payload(target, name)
        records.append(provenance_record(name, target, receipt, local_path=f"extracted/{name}"))

    metadata: dict[str, object] = {
        "acquisition_method": method,
        "resolution": resolution,
        "dryad_authentication": auth_mode,
        "transport": "authenticated_api" if auth_headers else "public_file_stream",
    }
    if resolution_error:
        metadata["resolution_warning"] = resolution_error
    return records, metadata

def _copy_expected_from_tree(source: Path, destination: Path, expected: list[str]) -> list[dict[str, object]]:
    by_name: dict[str, list[Path]] = {}
    for path in source.rglob("*"):
        if path.is_file():
            by_name.setdefault(path.name, []).append(path)

    missing = [name for name in expected if name not in by_name]
    duplicates = [name for name in expected if len(by_name.get(name, [])) > 1]
    if missing:
        raise AcquisitionError("archive incomplète, fichiers absents: " + ", ".join(missing))
    if duplicates:
        raise AcquisitionError("archive ambiguë, noms dupliqués: " + ", ".join(duplicates))

    destination.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for name in expected:
        target = destination / name
        shutil.copy2(by_name[name][0], target)
        validate_payload(target, name)
        records.append(provenance_record(name, target, local_path=f"extracted/{name}"))
    return records


def acquire_archive(
    dataset: dict[str, object],
    staging: Path,
    *,
    retries: int,
    timeout: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    archive_name = str(dataset["archive_name"])
    raw = staging / "raw" / archive_name
    headers = None
    auth_mode = "none"
    if str(dataset.get("provider", "")).lower() == "dryad":
        headers, auth_mode = dryad_auth_headers(timeout=timeout)
    receipt = download(
        str(dataset["download_url"]),
        raw,
        retries=retries,
        timeout=timeout,
        headers=headers,
    )
    validate_payload(raw, archive_name)

    unpacked = staging / "archive-content"
    unpacked.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(raw):
        archive_members = safe_extract_zip(raw, unpacked)
    else:
        copied = unpacked / raw.name
        shutil.copy2(raw, copied)
        archive_members = [copied.name]

    expected = [str(name) for name in dataset.get("expected_files", [])]
    records = _copy_expected_from_tree(unpacked, staging / "extracted", expected)
    return records, {
        "acquisition_method": "dataset_archive",
        "archive_provenance": provenance_record(
            archive_name, raw, receipt, local_path=f"raw/{archive_name}"
        ),
        "archive_members": archive_members,
        "dryad_authentication": auth_mode if str(dataset.get("provider", "")).lower() == "dryad" else "not_applicable",
    }


def inspect_cache(dataset: dict[str, object], folder: Path) -> tuple[bool, list[dict[str, object]], list[str]]:
    extracted_root = folder / "extracted"
    expected = [str(name) for name in dataset.get("expected_files", [])]
    records: list[dict[str, object]] = []
    errors: list[str] = []
    for name in expected:
        path = extracted_root / name
        try:
            validate_payload(path, name)
            records.append(provenance_record(name, path))
        except AcquisitionError as exc:
            errors.append(str(exc))
    return not errors and len(records) == len(expected), records, errors


def _remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def commit_staging(folder: Path, staging: Path) -> None:
    """Remplace données, archive et provenance dans une même transaction locale."""
    components = ("extracted", "raw", "SOURCE.json")
    backups: dict[str, Path] = {}
    installed: list[Path] = []
    try:
        for name in components:
            target = folder / name
            backup = folder / f".{name}.previous"
            _remove_path(backup)
            if target.exists():
                target.replace(backup)
                backups[name] = backup

        for name in components:
            source = staging / name
            target = folder / name
            if source.exists():
                source.replace(target)
                installed.append(target)

        for backup in backups.values():
            _remove_path(backup)
    except Exception:
        for target in installed:
            _remove_path(target)
        for name, backup in backups.items():
            target = folder / name
            if backup.exists():
                backup.replace(target)
        raise


def write_json_atomic(path: Path, document: object) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _error_document(exc: Exception, method: str) -> dict[str, object]:
    if isinstance(exc, AcquisitionError):
        result = exc.as_dict()
    else:
        result = {"error": f"{type(exc).__name__}: {exc}"}
    result["method"] = method
    return result


def acquire_dataset(
    dataset: dict[str, object],
    *,
    force: bool,
    offline: bool,
    retries: int,
    timeout: int,
) -> dict[str, object]:
    dataset_id = str(dataset["id"])
    folder = DEST / dataset_id
    folder.mkdir(parents=True, exist_ok=True)
    cache_ok, cache_records, cache_errors = inspect_cache(dataset, folder)

    if cache_ok and (not force or offline):
        return {
            "id": dataset_id,
            "required": bool(dataset.get("required_for_current_tests", False)),
            "status": "ok",
            "acquisition_state": "cached",
            "sha256": combined_sha256(cache_records),
            "size_bytes": sum(int(item["size_bytes"]) for item in cache_records),
            "files": len(cache_records),
        }
    if offline:
        return {
            "id": dataset_id,
            "required": bool(dataset.get("required_for_current_tests", False)),
            "status": "download_failed",
            "acquisition_state": "offline_cache_missing_or_invalid",
            "errors": cache_errors,
        }

    staging = prepare_staging(folder)
    attempts: list[dict[str, object]] = []
    records: list[dict[str, object]] | None = None
    metadata: dict[str, object] | None = None
    provider = str(dataset.get("provider", "")).lower()

    if provider == "dryad" or "datadryad.org" in str(dataset.get("landing_page", "")):
        try:
            records, metadata = acquire_individual_files(
                dataset,
                staging,
                retries=retries,
                timeout=timeout,
            )
        except Exception as exc:
            attempts.append(_error_document(exc, "dryad_individual_files"))
            staging = prepare_staging(folder)
            try:
                records, metadata = acquire_archive(
                    dataset,
                    staging,
                    retries=retries,
                    timeout=timeout,
                )
            except Exception as archive_exc:
                attempts.append(_error_document(archive_exc, "dataset_archive"))
    else:
        try:
            records, metadata = acquire_archive(
                dataset,
                staging,
                retries=retries,
                timeout=timeout,
            )
        except Exception as exc:
            attempts.append(_error_document(exc, "dataset_archive"))

    if records is None or metadata is None:
        shutil.rmtree(staging, ignore_errors=True)
        if cache_ok:
            return {
                "id": dataset_id,
                "required": bool(dataset.get("required_for_current_tests", False)),
                "status": "ok",
                "acquisition_state": "cached_after_refresh_failure",
                "warning": "le rafraîchissement a échoué, le cache complet antérieur est conservé",
                "attempt_errors": attempts,
                "sha256": combined_sha256(cache_records),
                "size_bytes": sum(int(item["size_bytes"]) for item in cache_records),
                "files": len(cache_records),
            }
        return {
            "id": dataset_id,
            "required": bool(dataset.get("required_for_current_tests", False)),
            "status": "download_failed",
            "acquisition_state": "no_valid_cache",
            "attempt_errors": attempts,
            "cache_errors": cache_errors,
            "url": dataset.get("download_url"),
        }

    extracted_files = sorted(item["name"] for item in records)
    provenance = {
        **dataset,
        **metadata,
        "download_status": "refreshed" if cache_ok else "downloaded",
        "sha256": combined_sha256(records),
        "size_bytes": sum(int(item["size_bytes"]) for item in records),
        "file_provenance": records,
        "extracted_files": extracted_files,
        "missing_expected": [],
        "prior_attempt_errors": attempts,
    }
    write_json_atomic(staging / "SOURCE.json", provenance)
    commit_staging(folder, staging)
    shutil.rmtree(staging, ignore_errors=True)
    return {
        "id": dataset_id,
        "required": bool(dataset.get("required_for_current_tests", False)),
        "status": "ok",
        "acquisition_state": provenance["download_status"],
        "acquisition_method": metadata["acquisition_method"],
        "missing": [],
        "sha256": provenance["sha256"],
        "size_bytes": provenance["size_bytes"],
        "files": len(records),
        "prior_attempt_errors": attempts,
    }



def blocking_failures(
    report: list[dict[str, object]],
    *,
    strict_optional: bool = False,
    allow_unavailable_required: bool = False,
) -> list[dict[str, object]]:
    """Retourne les échecs qui doivent réellement arrêter l'exécution.

    Une indisponibilité d'un fournisseur externe peut être tolérée dans une
    exécution CI ordinaire. Le rapport reste complet et les analyses dépendantes
    demeurent explicitement en attente. Le mode strict reste disponible.
    """
    return [
        item
        for item in report
        if item.get("status") != "ok"
        and (
            strict_optional
            or (
                bool(item.get("required"))
                and not allow_unavailable_required
            )
        )
    ]



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="Identifiant d'un jeu à télécharger")
    parser.add_argument("--force", action="store_true", help="Rafraîchir même si un cache complet existe")
    parser.add_argument("--offline", action="store_true", help="Contrôler uniquement le cache local")
    parser.add_argument("--strict-optional", action="store_true", help="Échouer aussi pour un jeu optionnel")
    parser.add_argument(
        "--allow-unavailable-required",
        action="store_true",
        help=(
            "Conserver les échecs des jeux requis dans le rapport sans arrêter "
            "l'exécution, utile lorsque le fournisseur externe bloque le runner CI"
        ),
    )
    parser.add_argument("--retries", type=int, default=4, help="Nombre de tentatives HTTP par URL")
    parser.add_argument("--timeout", type=int, default=300, help="Délai maximal par requête, en secondes")
    args = parser.parse_args(argv)

    if args.retries < 1:
        parser.error("--retries doit être supérieur ou égal à 1")
    if args.timeout < 1:
        parser.error("--timeout doit être supérieur ou égal à 1")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    datasets = registry.get("datasets", [])
    if not isinstance(datasets, list):
        raise SystemExit("registre invalide: datasets doit être une liste")
    selected = set(args.only or [])
    known = {str(item.get("id")) for item in datasets if isinstance(item, dict)}
    unknown = sorted(selected - known)
    if unknown:
        raise SystemExit("identifiant(s) inconnu(s): " + ", ".join(unknown))

    DEST.mkdir(exist_ok=True)
    report: list[dict[str, object]] = []
    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue
        if selected and str(dataset.get("id")) not in selected:
            continue
        result = acquire_dataset(
            dataset,
            force=args.force,
            offline=args.offline,
            retries=args.retries,
            timeout=args.timeout,
        )
        report.append(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    write_json_atomic(DEST / "ACQUISITION_REPORT.json", report)
    blocking = blocking_failures(
        report,
        strict_optional=args.strict_optional,
        allow_unavailable_required=args.allow_unavailable_required,
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
