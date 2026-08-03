# -*- coding: utf-8 -*-
"""
Figure 1 corrigée — Continuité des architectures matérielles et planétaires
jusqu'au raccord avec la branche vivant.

Corrections de grammaire par rapport à la version PDF :
  - H2/HD et 26Al ne sont plus dans l'épine dorsale : ce sont des CONDITIONS
    d'ouverture latérales (ambre, tireté) entrant dans une transition, sans
    filiation matérielle.
  - « Inventaire accessible » n'est plus une étape traversée : c'est une
    MÉTRIQUE DÉRIVÉE (vert, pointillé) LUE sur les réservoirs (liens de lecture).
  - Le « recyclage / remise en circulation » est une RÉTROACTION (double flèche)
    et non une étape supplémentaire.
  - L'épine reste une suite de FILIATIONS matérielles ; le seul mécanisme
    explicité comme noeud est « Accrétion, chauffage, fusion ».
"""
import style as S

W, H = 1020, 1360
CX = 430          # centre de l'épine (décalé pour dégager la gouttière des conditions)
NW, NH = 300, 66  # boîtes de l'épine

# (y_centre, type, titre, sous-titre)
SPINE = [
    (92,   "objet", "Constituants nucléaires", "protons, neutrons, noyaux"),
    (232,  "objet", "Atomes et molécules", "liaisons, réactivité, refroidissement"),
    (372,  "objet", "Grains, glaces et solides", "surfaces, adsorption, stockage"),
    (512,  "objet", "Agrégats et collectifs", "porosité, couplage aérodynamique"),
    (652,  "objet", "Planétésimaux", "gravité propre, intérieur, rétention"),
    (792,  "mecan", "Accrétion, chauffage, fusion", "différenciation métal-silicate"),
    (932,  "objet", "Réservoirs différenciés", "noyau, manteau, croûte, enveloppes"),
    (1072, "objet", "Interfaces réactives", "gradients eau-roche-gaz, cycles"),
    (1212, "objet", "Organisation chimique active", "raccord vers la branche vivant"),
]


def build():
    out = [S.header(W, H), S.defs()]

    # Titre discret
    out.append(f'<text x="34" y="42" font-size="19" font-weight="700" fill="{S.INK}">'
               f'Continuité des architectures — de la matière au vivant</text>')
    out.append(f'<text x="34" y="63" font-size="12.5" fill="#5a6b7a">'
               f'Épine de filiations matérielles ; conditions latérales ; inventaire lu, non traversé</text>')

    top = lambda yc: yc - NH/2
    xL = CX - NW/2
    xR = CX + NW/2

    # ---- Arêtes de filiation entre étages (dessinées avant les noeuds) ----
    for i in range(len(SPINE)-1):
        y1 = SPINE[i][0] + NH/2
        y2 = SPINE[i+1][0] - NH/2
        out.append(S.edge_filiation(f'M{CX},{y1} L{CX},{y2}'))

    # ---- CONDITION 1 : H2 / HD (refroidissement) -> transition Atomes -> Grains
    # cible : milieu de l'arête entre étage 2 (y=232) et 3 (y=372) ~ y=302
    c1x, c1y, c1w, c1h = 40, 268, 232, 62
    out.append(S.node_condition(c1x, c1y, c1w, c1h,
                                "H\u2082 / HD — refroidissement",
                                "condition, non filiation matérielle"))
    # lien condition depuis le bord droit du tag vers l'arête (x=CX, y~=302)
    out.append(S.edge_condition(f'M{c1x+c1w},{c1y+c1h/2} C{c1x+c1w+55},{c1y+c1h/2} '
                                f'{CX-70},302 {CX-4},302'))

    # ---- CONDITION 2 : 26Al . date d'accrétion (chauffage radiogénique)
    # cible : le noeud mécanisme « Accrétion, chauffage, fusion » (y=792)
    c2x, c2y, c2w, c2h = 40, 762, 232, 62
    out.append(S.node_condition(c2x, c2y, c2w, c2h,
                                "\u00b2\u2076Al \u00b7 date d'accrétion",
                                "chauffage radiogénique — condition"))
    out.append(S.edge_condition(f'M{c2x+c2w},{c2y+c2h/2} C{c2x+c2w+40},{c2y+c2h/2} '
                                f'{xL-30},792 {xL-4},792'))

    # ---- MÉTRIQUE : Inventaire accessible (lue sur les réservoirs) ----
    mx, my, mw, mh = 740, 902, 244, 128
    out.append(S.node_metrique(mx, my, mw, mh,
                               "Inventaire accessible",
                               "stock \u00b7 flux \u00b7 contrefactuel — mesure dérivée, non une étape"))
    # lectures pointillées depuis Réservoirs (y=932) et Interfaces (y=1072)
    out.append(S.edge_lecture(f'M{xR},932 C{xR+40},932 {mx-40},{my+42} {mx-4},{my+42}'))
    out.append(S.edge_lecture(f'M{xR},1072 C{xR+40},1072 {mx-40},{my+92} {mx-4},{my+92}'))

    # ---- COÉVOLUTION / recyclage : Interfaces (1072) <-> Accrétion/Réservoirs (792) ----
    fx = 640
    out.append(S.edge_coevolution(f'M{xR-14},1072 C{fx},1060 {fx},900 {xR-14},792'))
    out.append(S.edge_label(660, 940, "recyclage \u00b7 remise en circulation",
                            S.L_COE, anchor="middle"))

    # ---- Noeuds de l'épine ----
    for yc, typ, title, sub in SPINE:
        y = top(yc)
        if typ == "objet":
            out.append(S.node_objet(xL, y, NW, NH, title, sub))
        else:
            out.append(S.node_mecanisme(xL, y, NW, NH, title, sub))

    # ---- Petites étiquettes de transformation sur l'épine (discret) ----
    # côté droit en haut (libre), côté gauche en bas (évite lectures + coévolution)
    trans_right = [
        (162, "chimie électronique"),
        (302, "condensation, refroidissement"),
        (442, "coagulation, dérive"),
        (582, "concentration, effondrement"),
        (722, "gravité propre"),
        (862, "différenciation"),
    ]
    for ty, lbl in trans_right:
        out.append(S.edge_label(CX+9, ty+4, lbl, S.L_FIL, anchor="start", size=10.5))
    trans_left = [
        (1002, "circulation entre réservoirs"),
        (1142, "interfaces, cycles"),
    ]
    for ty, lbl in trans_left:
        out.append(S.edge_label(CX-9, ty+4, lbl, S.L_FIL, anchor="end", size=10.5))

    return "\n".join(out) + "\n</svg>\n"


if __name__ == "__main__":
    open("figure1.svg", "w").write(build())
    print("figure1.svg written")
