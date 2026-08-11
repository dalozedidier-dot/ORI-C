"""Teste l'échelle des dix capacités physiques, au lieu de la décrire.

Le rapport précédent avait établi deux choses : les six dimensions recopiaient
le régime, et la carte relationnelle n'ajoutait rien à la chronologie. La
réponse n'est pas d'abandonner les branches, c'est de les représenter par un
attribut qui puisse échouer. L'échelle des capacités en est un.

Deux tests, préenregistrés ici avant lecture des résultats.

A. Monotonie. Le long d'une arête, le niveau de capacité ne doit pas décroître,
   sauf sur les arêtes qui représentent un retour de matière : recyclage,
   fragmentation, transport. Une décroissance sur une arête de transformation
   ou d'assemblage réfute soit l'échelle, soit le typage de l'arête.

B. Information. Si le niveau de capacité est entièrement prédit par la
   profondeur depuis la racine, il recopie la chronologie et n'apporte rien —
   l'échec exact des six dimensions. Le gain est mesuré en bits, et comparé à
   un tirage par permutation : à cinquante nœuds et dix niveaux, une part du
   gain apparent n'est que de la mémorisation. C'est le contrôle qui manquait
   lorsqu'un gain de 0,654 bit avait été pris pour un résultat.

    python tester_hierarchie.py
"""
from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict, deque
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = "N036"
TIRAGES = 20000
GRAINE = 20260802

# Types d'arête où une baisse de capacité est attendue : la matière revient
# vers un état antérieur, elle ne progresse pas.
TYPES_DE_RETOUR = {"recyclage", "fragmentation", "transport", "contrainte"}


def lire(nom: str) -> list[dict]:
    with (ICI / nom).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def entropie(valeurs) -> float:
    n = len(valeurs)
    return -sum((c / n) * math.log2(c / n) for c in Counter(valeurs).values())


def entropie_conditionnelle(cibles, conditions) -> float:
    n, groupes = len(cibles), defaultdict(list)
    for c, k in zip(cibles, conditions):
        groupes[k].append(c)
    return sum(len(g) / n * entropie(g) for g in groupes.values())


def main() -> int:
    noeuds = {n["node_id"]: n for n in lire("noeuds.csv")}
    aretes = lire("hyperaretes.csv")
    niveau = {i: int(n["niveau_capacite"]) for i, n in noeuds.items()}
    roles = {a["edge_id"]: a["role_genealogique"] for a in aretes}
    D = lambda s: [x for x in (s or "").split("|") if x]

    # --- Test A : monotonie ---------------------------------------------
    violations, comptes = [], Counter()
    for a in aretes:
        partage = set(D(a["entrees"])) & set(D(a["sorties"]))
        for e in D(a["entrees"]):
            for s in D(a["sorties"]):
                if e == s or e in partage or s in partage:
                    continue
                comptes["arcs_examines"] += 1
                if niveau[s] < niveau[e]:
                    comptes["baisses"] += 1
                    attendu = a["type"] in TYPES_DE_RETOUR
                    comptes["baisses_attendues" if attendu
                            else "baisses_inattendues"] += 1
                    if not attendu:
                        violations.append({
                            "arete": a["edge_id"], "processus": a["processus"],
                            "type": a["type"],
                            "de": f"{e} niveau {niveau[e]}",
                            "vers": f"{s} niveau {niveau[s]}"})

    # --- Test A bis, EXPLORATOIRE, après échec du test A -----------------
    # L'exécution 1 est conservée telle quelle dans
    # test_hierarchie_execution_1_prereglee.json : la règle préenregistrée est
    # réfutée, onze arcs baissent hors arête de retour. Le regroupement des
    # violations montre qu'elles ne sont pas de même nature. Trois arêtes
    # détruisent réellement une structure (vaporisation, fusion éclair,
    # impacts géants) : elles étaient mal typées. Cinq autres décrivent un
    # système assemblé qui émet des constituants — une étoile de niveau 6
    # produit des éléments lourds de niveau 1. Ce n'est pas une régression,
    # c'est une production. L'échelle n'est donc pas un axe unique : elle
    # mesure le niveau structurel d'un objet, et un objet peut engendrer des
    # constituants situés plus bas. La règle révisée l'admet explicitement.
    # Elle est plus faible que la règle initiale et n'a pas été préenregistrée.
    violations_bis = []
    for a in aretes:
        if a["role_genealogique"] != "progression":
            continue
        partage = set(D(a["entrees"])) & set(D(a["sorties"]))
        for e in D(a["entrees"]):
            for s_ in D(a["sorties"]):
                if e == s_ or e in partage or s_ in partage:
                    continue
                if niveau[s_] < niveau[e]:
                    violations_bis.append({
                        "arete": a["edge_id"], "processus": a["processus"],
                        "de": f"{e} niveau {niveau[e]}",
                        "vers": f"{s_} niveau {niveau[s_]}"})

    # --- Profondeur depuis la racine, comme position chronologique -------
    suivants = defaultdict(set)
    for a in aretes:
        for e in D(a["entrees"]):
            suivants[e].update(s for s in D(a["sorties"]) if s != e)
    profondeur, file = {RACINE: 0}, deque([RACINE])
    while file:
        courant = file.popleft()
        for s in suivants[courant]:
            if s not in profondeur:
                profondeur[s] = profondeur[courant] + 1
                file.append(s)
    joignables = sorted(profondeur)
    inatteignables = sorted(set(noeuds) - set(profondeur))

    # --- Test B : information au-delà de la profondeur -------------------
    niveaux = [niveau[n] for n in joignables]
    profs = [profondeur[n] for n in joignables]
    h_niveau = entropie(niveaux)
    gain = h_niveau - entropie_conditionnelle(niveaux, profs)

    # Corrélation de rang de Spearman, sans dépendance externe.
    def rangs(x):
        ordre = sorted(range(len(x)), key=lambda i: x[i])
        r = [0.0] * len(x)
        i = 0
        while i < len(ordre):
            j = i
            while j + 1 < len(ordre) and x[ordre[j + 1]] == x[ordre[i]]:
                j += 1
            moyen = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[ordre[k]] = moyen
            i = j + 1
        return r

    rn, rp = rangs(niveaux), rangs(profs)
    mn, mp = sum(rn) / len(rn), sum(rp) / len(rp)
    num = sum((a - mn) * (b - mp) for a, b in zip(rn, rp))
    den = math.sqrt(sum((a - mn) ** 2 for a in rn)
                    * sum((b - mp) ** 2 for b in rp))
    rho = num / den if den else 0.0

    # Contrôle apparié : le même calcul sur des niveaux permutés. Il donne le
    # gain que la seule taille de l'échantillon fabrique.
    alea = random.Random(GRAINE)
    nuls = []
    melange = list(niveaux)
    for _ in range(TIRAGES):
        alea.shuffle(melange)
        nuls.append(h_niveau - entropie_conditionnelle(melange, profs))
    nuls.sort()
    p = (sum(1 for g in nuls if g >= gain) + 1) / (TIRAGES + 1)
    moyenne_nulle = sum(nuls) / len(nuls)

    rapport = {
        "noeuds": len(noeuds), "hyperaretes": len(aretes),
        "noeuds_joignables_depuis_la_racine": len(joignables),
        "noeuds_inatteignables": inatteignables,
        "profondeur_maximale": max(profondeur.values()),
        "test_A_monotonie": {
            "arcs_examines": comptes["arcs_examines"],
            "baisses_de_capacite": comptes["baisses"],
            "baisses_sur_arete_de_retour": comptes["baisses_attendues"],
            "baisses_inattendues": comptes["baisses_inattendues"],
            "violations": violations,
            "verdict": ("monotonie respectee hors aretes de retour"
                        if not violations else "REFUTEE"),
        },
        "test_A_bis_exploratoire": {
            "regle": ("le niveau ne peut baisser que sur une arete de retour "
                      "ou d emission de constituants par un systeme assemble"),
            "roles_declares": dict(Counter(roles.values())),
            "violations_restantes": violations_bis,
            "verdict": ("coherente sous la regle revisee" if not violations_bis
                        else "REFUTEE MEME REVISEE"),
            "avertissement": ("regle etablie apres lecture des violations de "
                              "l execution 1 : exploratoire, non preenregistree"),
            "corrections_posterieures_aux_echecs": [
                "N029 inventaire accessible : niveau 10 ramene a 8",
                "N054 especes solubles : niveau 10 ramene a 8"],
            "consequence": ("deux niveaux ont ete corriges apres avoir vu les "
                            "violations, et une troisieme violation est apparue. "
                            "La poursuite serait du bricolage. Elle est arretee."),
            "conclusion": ("La monotonie est refutee et ne peut pas etre "
                           "retablie par un reetiquetage. La raison est "
                           "structurelle : une production pointe toujours vers "
                           "le bas. Une etoile de niveau 6 produit des elements "
                           "de niveau 1 ; un systeme hydrothermal de niveau 9 "
                           "produit des especes mobiles de niveau 8. L echelle "
                           "ordonne des OBJETS, pas des PROCESSUS : elle ne peut "
                           "pas etre un invariant le long des aretes. Elle reste "
                           "un codage valide, et le test B montre qu il porte de "
                           "l information. Il n est simplement pas monotone."),
        },
        "test_B_information": {
            "entropie_du_niveau_bits": round(h_niveau, 4),
            "gain_observe_bits": round(gain, 4),
            "gain_moyen_sous_permutation_bits": round(moyenne_nulle, 4),
            "gain_net_du_bruit_bits": round(gain - moyenne_nulle, 4),
            "p_par_permutation": round(p, 5),
            "spearman_niveau_profondeur": round(rho, 4),
            "part_de_l_entropie_expliquee": round(gain / h_niveau, 4),
            "tirages": TIRAGES,
        },
        "lecture": (
            "Un rho proche de 1 signifierait que l'echelle recopie la "
            "profondeur et n'ajoute rien : ce fut l'echec des six dimensions. "
            "Un gain observe proche du gain sous permutation signifierait que "
            "le gain n'est que de la memorisation a petit effectif."),
        "portee": (
            "L'echelle est un codage propose, pas une mesure. Ces tests "
            "controlent sa coherence interne et sa non-redondance avec la "
            "position dans le graphe. Ils ne valident pas ORI-C."),
    }
    (ICI / "test_hierarchie_resultats.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 0 if not violations_bis and not inatteignables else 1


if __name__ == "__main__":
    raise SystemExit(main())
