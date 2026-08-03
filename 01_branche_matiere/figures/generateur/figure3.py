# -*- coding: utf-8 -*-
"""Figure 3 — Succession de la branche 1 (briques et architectures matérielles).
Grammaire corrigée : le refroidissement H2/HD est une CONDITION latérale (non
filiation) ; l'inventaire baryonique est une CONTRAINTE de quantité (tag latéral) ;
les signatures présolaires sont une TRANSMISSION DE TRACE (violet) des grains vers
le réservoir nuage-disque ; l'épine reste une suite de filiations matérielles,
disposée en boustrophédon (aller-retour) pour tenir la continuité sur une page."""
import style as S

W, H = 1300, 750
NW, NH = 214, 60

# 3 rangées, 4 colonnes. Centres de colonnes :
COL = [280, 545, 810, 1075]
ROWY = [156, 388, 620]

def box(col, row):
    cx = COL[col]
    cy = ROWY[row]
    return cx - NW/2, cy - NH/2, cx, cy

def build():
    out = [S.header(W, H), S.defs()]
    out.append(f'<text x="34" y="40" font-size="19" font-weight="700" fill="{S.INK}">'
               f'Branche 1 \u2014 des constituants nucléaires aux planétésimaux</text>')

    # ----- Noeuds de l'épine (col,row,titre,sous-titre) -----
    spine = [
        (0,0,"Protons, neutrons et noyaux","assemblages nucléaires durables"),
        (1,0,"Noyaux légers","nucléosynthèse"),
        (2,0,"Atomes","chimie électronique"),
        (3,0,"Effondrement","premières structures"),
        (3,1,"Premières étoiles","fusion, enrichissement"),
        (2,1,"Éjecta stellaires","vents, explosions"),
        (1,1,"Milieu interstellaire","réservoir composite, mélange"),
        (0,1,"Nuage / disque protosolaire","réservoir initial"),
        (0,2,"Grains et glaces","hérités + condensés"),
        (1,2,"Retraitement","inclusions, chondres"),
        (2,2,"Agrégats et galets","collectif, dérive, pièges"),
        (3,2,"Planétésimaux","gravité propre, histoire locale"),
    ]

    # ----- Filiations : chemin en boustrophédon -----
    seq = [(0,0),(1,0),(2,0),(3,0),(3,1),(2,1),(1,1),(0,1),(0,2),(1,2),(2,2),(3,2)]
    def center(cell): return COL[cell[0]], ROWY[cell[1]]
    for a, b in zip(seq, seq[1:]):
        (ax, ay), (bx, by) = center(a), center(b)
        if ay == by:  # horizontal
            if bx > ax:   # vers la droite
                out.append(S.edge_filiation(f'M{ax+NW/2},{ay} L{bx-NW/2},{by}'))
            else:         # vers la gauche
                out.append(S.edge_filiation(f'M{ax-NW/2},{ay} L{bx+NW/2},{by}'))
        else:  # descente de rangée
            out.append(S.edge_filiation(f'M{ax},{ay+NH/2} L{bx},{by-NH/2}'))

    # ----- CONTRAINTE : inventaire baryonique (tag ambre) -> chaîne nucléaire -----
    cbx, cby, cbw, cbh = 70, 48, 216, 56
    out.append(S.node_condition(cbx, cby, cbw, cbh, "Inventaire baryonique",
                                "contrainte de quantité"))
    _,_, bx, by = box(1,0)
    out.append(S.edge_condition(f'M{cbx+cbw/2},{cby+cbh} C{cbx+cbw/2},{cby+cbh+30} '
                                f'{bx},{by-NH/2-30} {bx},{by-NH/2-2}'))

    # ----- CONDITION : H2/HD refroidissement -> effondrement -----
    hx, hy, hw, hh = 967, 48, 216, 56
    out.append(S.node_condition(hx, hy, hw, hh, "H\u2082 / HD \u2014 refroidissement",
                                "condition, non filiation"))
    _,_, dx, dy = box(3,0)
    out.append(S.edge_condition(f'M{hx+hw/2},{hy+hh} C{hx+hw/2},{hy+hh+30} '
                                f'{dx},{dy-NH/2-30} {dx},{dy-NH/2-2}'))

    # ----- TRACE : signatures présolaires, grains -> nuage/disque (boucle à gauche) -----
    _,_, gx, gy = box(0,2)     # grains (bas gauche)
    _,_, nx, ny = box(0,1)     # nuage/disque (milieu gauche)
    loopx = gx - NW/2 - 64
    out.append(S.edge_trace(f'M{gx-NW/2},{gy-8} C{loopx},{gy-30} '
                            f'{loopx},{ny+30} {nx-NW/2},{ny+8}'))
    lblx = loopx - 12
    lbly = (gy + ny) / 2
    out.append(f'<text x="{lblx:.0f}" y="{lbly:.0f}" text-anchor="middle" '
               f'font-size="10.5" font-style="italic" fill="{S.L_TRA}" '
               f'transform="rotate(-90 {lblx:.0f} {lbly:.0f})">'
               f'signatures présolaires</text>')

    # ----- Noeuds (dessinés au-dessus des liens) -----
    for col,row,title,sub in spine:
        x,y,_,_ = box(col,row)
        out.append(S.node_objet(x, y, NW, NH, title, sub))

    return "\n".join(out) + "\n</svg>\n"

if __name__ == "__main__":
    open("figure3.svg", "w").write(build())
    print("figure3.svg written")
