from __future__ import annotations

import importlib.util
import io
import json
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "plan_directeur/campagne_recherche_suivante/fetch_external_data.py"


def load_module():
    specification = importlib.util.spec_from_file_location("fetch_external_data_tested", MODULE_PATH)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


class LocalServer:
    def __init__(self, handler: type[BaseHTTPRequestHandler]) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> str:
        self.thread.start()
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def test_download_preserves_signed_redirect_path(tmp_path):
    module = load_module()
    exact_path = "/signed/%2Fkeep%2Bvalue?token=a%2Fb"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            if self.path == "/start":
                self.send_response(302)
                self.send_header("Location", exact_path)
                self.end_headers()
                return
            if self.path == exact_path:
                payload = b"x,y\n1,2\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            self.send_response(403)
            self.end_headers()

    with LocalServer(Handler) as base:
        target = tmp_path / "data.csv"
        receipt = module.download(f"{base}/start", target, retries=1, timeout=10)

    assert target.read_bytes() == b"x,y\n1,2\n"
    assert receipt["redirects"][-1].endswith(exact_path)
    assert receipt["http_status"] == 200


def test_safe_extract_rejects_path_traversal(tmp_path):
    module = load_module()
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("../escape.txt", "interdit")

    with pytest.raises(module.AcquisitionError, match="chemin interdit"):
        module.safe_extract_zip(archive, tmp_path / "out")
    assert not (tmp_path / "escape.txt").exists()


def test_validate_payload_rejects_html_disguised_as_xlsx(tmp_path):
    module = load_module()
    fake = tmp_path / "result.xlsx"
    fake.write_text("<!doctype html><html>Access denied</html>", encoding="utf-8")
    with pytest.raises(module.AcquisitionError, match="HTML/XML"):
        module.validate_payload(fake, "result.xlsx")


def test_dryad_individual_failure_falls_back_to_archive(tmp_path, monkeypatch):
    module = load_module()
    module.DEST = tmp_path / "external"
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as handle:
        handle.writestr("nested/expected.csv", "a,b\n1,2\n")
    archive_bytes = archive_buffer.getvalue()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            if self.path == "/bad.csv":
                self.send_response(403)
                self.end_headers()
                return
            if self.path == "/dataset.zip":
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Length", str(len(archive_bytes)))
                self.end_headers()
                self.wfile.write(archive_bytes)
                return
            self.send_response(404)
            self.end_headers()

    with LocalServer(Handler) as base:
        monkeypatch.setattr(
            module,
            "resolve_dryad_files",
            lambda dataset, timeout: (
                {"expected.csv": f"{base}/bad.csv"},
                {"provider": "dryad", "version_number": 1},
            ),
        )
        dataset = {
            "id": "dryad_fixture",
            "provider": "dryad",
            "doi": "10.5061/dryad.fixture",
            "landing_page": f"{base}/landing",
            "download_url": f"{base}/dataset.zip",
            "archive_name": "dataset.zip",
            "expected_files": ["expected.csv"],
            "required_for_current_tests": True,
            "redistribute": False,
        }
        result = module.acquire_dataset(
            dataset,
            force=True,
            offline=False,
            retries=1,
            timeout=10,
        )

    assert result["status"] == "ok"
    assert result["acquisition_method"] == "dataset_archive"
    assert len(result["prior_attempt_errors"]) == 1
    extracted = module.DEST / "dryad_fixture/extracted/expected.csv"
    assert extracted.read_text(encoding="utf-8") == "a,b\n1,2\n"
    source = json.loads((module.DEST / "dryad_fixture/SOURCE.json").read_text(encoding="utf-8"))
    assert source["missing_expected"] == []
    assert source["acquisition_method"] == "dataset_archive"


def test_failed_refresh_preserves_complete_cache(tmp_path, monkeypatch):
    module = load_module()
    module.DEST = tmp_path / "external"
    cached = module.DEST / "dryad_fixture/extracted/expected.csv"
    cached.parent.mkdir(parents=True)
    cached.write_text("a,b\n9,8\n", encoding="utf-8")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            self.send_response(503)
            self.end_headers()

    with LocalServer(Handler) as base:
        monkeypatch.setattr(
            module,
            "resolve_dryad_files",
            lambda dataset, timeout: (
                {"expected.csv": f"{base}/failed"},
                {"provider": "dryad"},
            ),
        )
        dataset = {
            "id": "dryad_fixture",
            "provider": "dryad",
            "doi": "10.5061/dryad.fixture",
            "landing_page": f"{base}/landing",
            "download_url": f"{base}/failed",
            "archive_name": "dataset.zip",
            "expected_files": ["expected.csv"],
            "required_for_current_tests": True,
            "redistribute": False,
        }
        result = module.acquire_dataset(
            dataset,
            force=True,
            offline=False,
            retries=1,
            timeout=10,
        )

    assert result["status"] == "ok"
    assert result["acquisition_state"] == "cached_after_refresh_failure"
    assert cached.read_text(encoding="utf-8") == "a,b\n9,8\n"


def test_resolve_dryad_files_uses_current_version_file_ids(monkeypatch):
    module = load_module()
    dataset = {
        "doi": "10.5061/dryad.fixture",
        "expected_files": ["expected.csv"],
    }

    def fake_fetch_json(url, timeout):
        return (
            {"_links": {"stash:versions": {"href": "/api/v2/fixture/versions"}}},
            {"final_url": url, "http_status": 200},
        )

    def fake_paginate(url, embedded_names, timeout, max_pages=100):
        if "stash:versions" in embedded_names:
            return [
                {
                    "id": 10,
                    "versionNumber": 1,
                    "versionStatus": "submitted",
                    "_links": {"stash:files": {"href": "/api/v2/versions/10/files"}},
                },
                {
                    "id": 20,
                    "versionNumber": 2,
                    "versionStatus": "submitted",
                    "_links": {"stash:files": {"href": "/api/v2/versions/20/files"}},
                },
            ]
        return [
            {
                "path": "nested/expected.csv",
                "_links": {"self": {"href": "/api/v2/files/987654"}},
            }
        ]

    monkeypatch.setattr(module, "fetch_json", fake_fetch_json)
    monkeypatch.setattr(module, "paginate_json", fake_paginate)
    urls, resolution = module.resolve_dryad_files(dataset, timeout=10)

    assert urls == {"expected.csv": "https://datadryad.org/downloads/file_stream/987654"}
    assert resolution["version_number"] == 2
    assert resolution["resolved_file_ids"] == {"expected.csv": "987654"}


def test_dryad_auth_headers_uses_client_credentials(monkeypatch):
    module = load_module()
    monkeypatch.delenv("DRYAD_API_TOKEN", raising=False)
    monkeypatch.setenv("DRYAD_API_CLIENT_ID", "client-id")
    monkeypatch.setenv("DRYAD_API_CLIENT_SECRET", "client-secret")
    monkeypatch.setattr(
        module,
        "_oauth_token_request",
        lambda client_id, client_secret, timeout: "issued-token",
    )

    headers, mode = module.dryad_auth_headers(timeout=10)

    assert mode == "client_credentials"
    assert headers == {"Authorization": "Bearer issued-token", "Accept": "*/*"}


def test_authenticated_dryad_download_uses_api_endpoint(tmp_path, monkeypatch):
    module = load_module()
    dataset = {
        "id": "dryad_fixture",
        "provider": "dryad",
        "doi": "10.5061/dryad.fixture",
        "landing_page": "https://datadryad.org/dataset/doi:10.5061/dryad.fixture",
        "expected_files": ["expected.csv"],
    }
    monkeypatch.setattr(
        module,
        "resolve_dryad_files",
        lambda dataset, timeout: (
            {"expected.csv": "https://datadryad.org/downloads/file_stream/987654"},
            {"provider": "dryad", "resolved_file_ids": {"expected.csv": "987654"}},
        ),
    )
    monkeypatch.setattr(
        module,
        "dryad_auth_headers",
        lambda timeout: ({"Authorization": "Bearer test-token", "Accept": "*/*"}, "client_credentials"),
    )
    calls = []

    def fake_download(url, target, retries, timeout, headers=None):
        calls.append((url, headers))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("a,b\n1,2\n", encoding="utf-8")
        return {
            "requested_url": url,
            "final_url": url,
            "http_status": 200,
            "content_type": "text/csv",
            "redirects": [],
            "sha256": module.sha256(target),
            "size_bytes": target.stat().st_size,
            "attempts": 1,
        }

    monkeypatch.setattr(module, "download", fake_download)
    records, metadata = module.acquire_individual_files(
        dataset,
        tmp_path / "staging",
        retries=1,
        timeout=10,
    )

    assert calls == [
        (
            "https://datadryad.org/api/v2/files/987654/download",
            {"Authorization": "Bearer test-token", "Accept": "*/*"},
        )
    ]
    assert metadata["dryad_authentication"] == "client_credentials"
    assert metadata["transport"] == "authenticated_api"
    assert records[0]["name"] == "expected.csv"



def test_public_dryad_download_uses_file_stream_without_credentials(tmp_path, monkeypatch):
    module = load_module()
    dataset = {
        "id": "dryad_fixture",
        "provider": "dryad",
        "doi": "10.5061/dryad.fixture",
        "landing_page": "https://datadryad.org/dataset/doi:10.5061/dryad.fixture",
        "expected_files": ["expected.csv"],
    }
    monkeypatch.setattr(
        module,
        "resolve_dryad_files",
        lambda dataset, timeout: (
            {"expected.csv": "https://datadryad.org/downloads/file_stream/987654"},
            {"provider": "dryad", "resolved_file_ids": {"expected.csv": "987654"}},
        ),
    )
    monkeypatch.setattr(module, "dryad_auth_headers", lambda timeout: (None, "none"))
    calls = []

    def fake_download(url, target, retries, timeout, headers=None):
        calls.append((url, headers))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("a,b\n1,2\n", encoding="utf-8")
        return {
            "requested_url": url,
            "final_url": url,
            "http_status": 200,
            "content_type": "text/csv",
            "redirects": [],
            "sha256": module.sha256(target),
            "size_bytes": target.stat().st_size,
            "attempts": 1,
        }

    monkeypatch.setattr(module, "download", fake_download)
    records, metadata = module.acquire_individual_files(
        dataset,
        tmp_path / "staging",
        retries=1,
        timeout=10,
    )

    assert calls == [
        ("https://datadryad.org/downloads/file_stream/987654", None)
    ]
    assert metadata["dryad_authentication"] == "none"
    assert metadata["transport"] == "public_file_stream"
    assert records[0]["name"] == "expected.csv"



def test_download_forwards_authorization_header(tmp_path):
    module = load_module()
    observed = {"authorization": ""}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            observed["authorization"] = self.headers.get("Authorization", "")
            if observed["authorization"] != "Bearer fixture-token":
                self.send_response(401)
                self.end_headers()
                return
            payload = b"a,b\n1,2\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    with LocalServer(Handler) as base:
        target = tmp_path / "expected.csv"
        receipt = module.download(
            f"{base}/api/v2/files/1/download",
            target,
            retries=1,
            timeout=10,
            headers={"Authorization": "Bearer fixture-token"},
        )

    assert observed["authorization"] == "Bearer fixture-token"
    assert target.read_text(encoding="utf-8") == "a,b\n1,2\n"
    assert receipt["http_status"] == 200


def test_authorization_is_removed_on_cross_origin_redirect(tmp_path):
    module = load_module()
    observed = {"start": "", "final": ""}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            if self.path == "/start":
                observed["start"] = self.headers.get("Authorization", "")
                host, port = self.server.server_address
                self.send_response(302)
                self.send_header("Location", f"http://localhost:{port}/final")
                self.end_headers()
                return
            if self.path == "/final":
                observed["final"] = self.headers.get("Authorization", "")
                payload = b"a,b\n1,2\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            self.send_response(404)
            self.end_headers()

    with LocalServer(Handler) as base:
        target = tmp_path / "expected.csv"
        module.download(
            f"{base}/start",
            target,
            retries=1,
            timeout=10,
            headers={"Authorization": "Bearer fixture-token"},
        )

    assert observed["start"] == "Bearer fixture-token"
    assert observed["final"] == ""
    assert target.read_text(encoding="utf-8") == "a,b\n1,2\n"


def test_blocking_failures_can_tolerate_external_unavailability():
    module = load_module()
    report = [
        {"id": "required", "required": True, "status": "download_failed"},
        {"id": "optional", "required": False, "status": "download_failed"},
    ]

    strict = module.blocking_failures(report)
    tolerant = module.blocking_failures(
        report,
        allow_unavailable_required=True,
    )
    strict_all = module.blocking_failures(
        report,
        allow_unavailable_required=True,
        strict_optional=True,
    )

    assert [item["id"] for item in strict] == ["required"]
    assert tolerant == []
    assert [item["id"] for item in strict_all] == ["required", "optional"]
