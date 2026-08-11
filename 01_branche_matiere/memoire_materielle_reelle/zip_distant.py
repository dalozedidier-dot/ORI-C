#!/usr/bin/env python3
"""Lit une archive ZIP distante par requêtes de plage, sans la rapatrier.

Un enregistrement Zenodo livre souvent une seule archive de plusieurs gigaoctets
dont un test ne lit qu'un fichier. Le format ZIP place son index à la fin :
quelques dizaines de kilooctets suffisent à connaître la liste des membres, puis
chaque membre voulu se récupère par sa plage d'octets.

    from zip_distant import membres, extraire
    for nom, taille in membres(url):
        ...
    donnees = extraire(url, "chemin/dans/archive.csv")
"""
from __future__ import annotations

import io
import urllib.request
import zipfile

FIN = 1 << 16
BLOC = 1 << 20


class FichierDistant(io.RawIOBase):
    """Objet fichier en lecture seule adossé à des requêtes `Range`."""

    def __init__(self, url: str, timeout: int = 120):
        self.url = url
        self.timeout = timeout
        self._position = 0
        self._taille = self._interroger_taille()

    def _interroger_taille(self) -> int:
        requete = urllib.request.Request(self.url, method="HEAD")
        with urllib.request.urlopen(requete, timeout=self.timeout) as reponse:
            longueur = reponse.headers.get("Content-Length")
            if longueur is None:
                raise OSError("le serveur n'annonce pas Content-Length")
            return int(longueur)

    def _lire_plage(self, debut: int, longueur: int) -> bytes:
        if longueur <= 0:
            return b""
        fin = min(debut + longueur, self._taille) - 1
        requete = urllib.request.Request(self.url)
        requete.add_header("Range", f"bytes={debut}-{fin}")
        with urllib.request.urlopen(requete, timeout=self.timeout) as reponse:
            if reponse.status != 206:
                raise OSError("le serveur ignore les requêtes de plage")
            return reponse.read()

    # --- interface fichier ---
    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def seek(self, decalage: int, origine: int = io.SEEK_SET) -> int:
        if origine == io.SEEK_SET:
            self._position = decalage
        elif origine == io.SEEK_CUR:
            self._position += decalage
        else:
            self._position = self._taille + decalage
        return self._position

    def tell(self) -> int:
        return self._position

    def read(self, taille: int = -1) -> bytes:
        if taille < 0:
            taille = self._taille - self._position
        donnees = self._lire_plage(self._position, taille)
        self._position += len(donnees)
        return donnees

    def readinto(self, tampon) -> int:
        donnees = self.read(len(tampon))
        tampon[:len(donnees)] = donnees
        return len(donnees)


def membres(url: str) -> list[tuple[str, int, int]]:
    """Nom, taille décompressée et taille compressée de chaque membre."""
    with zipfile.ZipFile(FichierDistant(url)) as archive:
        return [(i.filename, i.file_size, i.compress_size)
                for i in archive.infolist() if not i.is_dir()]


def extraire(url: str, noms: list[str]) -> dict[str, bytes]:
    """Contenu des membres demandés, récupérés par leurs seules plages."""
    resultats: dict[str, bytes] = {}
    distant = FichierDistant(url)
    with zipfile.ZipFile(distant) as archive:
        for nom in noms:
            with archive.open(nom) as flux:
                resultats[nom] = flux.read()
    return resultats
