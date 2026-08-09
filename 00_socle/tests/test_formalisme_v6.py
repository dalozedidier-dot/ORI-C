from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_codebook_distingue_echelles_regimes_et_raccords() -> None:
    codebook = read("00_socle/CODEBOOK.md")

    for notation in (
        "ℓ_ana",
        "{ℓ_phys}",
        "(D_i,G_i)",
        "Ω_Gi(S(t0))",
        "T(i→j)",
        "information conservée, abandonnée et éventuellement reconstruite",
    ):
        assert notation in codebook


def test_codebook_definit_mise_a_jour_et_persistance_vectorielle() -> None:
    codebook = read("00_socle/CODEBOOK.md")

    assert "S(t1) = U_i[t0,t1 ; S(t0), h_i]" in codebook
    assert "P_pers[h] = (P_1[h], ..., P_n[h])" in codebook
    assert "Π* = (Π_1*, ..., Π_n*)" in codebook
    assert "Q(P_pers[h], Π*)" in codebook
    assert "mesure **locale**" in codebook


def test_architecture_decrit_une_boucle_recursive() -> None:
    architecture = read("ARCHITECTURE.md")

    assert "boucle canonique" in architecture
    assert "S(t1) = U_i[t0,t1 ; S(t0),h_i]" in architecture
    assert "nouveaux possibles → itération suivante" in architecture


def test_protocole_preserve_les_donnees_existantes() -> None:
    protocole = read("00_socle/PROTOCOLE_DONNEES.md")

    assert "rétroactivement comme exigences" in protocole
    assert "La mesure historique `Π_pers" in protocole
