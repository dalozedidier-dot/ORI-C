# -*- coding: utf-8 -*-
"""Figure 5 — Stock, flux et variation contrefactuelle : trois niveaux de mesure
du MÊME inventaire, lus sur un réservoir. Point de grammaire : AUCUNE succession
causale entre les trois (pas de flèche de l'un vers l'autre) ; chacun est une
métrique dérivée (vert, pointillé) reliée au réservoir par un lien de lecture."""
import style as S

W, H = 1000, 520

def build():
    out = [S.header(W, H), S.defs()]
    out.append(f'<text x="34" y="42" font-size="19" font-weight="700" fill="{S.INK}">'
               f'Trois niveaux de mesure du même inventaire</text>')
    out.append(f'<text x="34" y="63" font-size="12.5" fill="#5a6b7a">'
               f'Lus sur un réservoir \u2014 aucune succession causale entre eux</text>')

    # Réservoir (objet) à gauche
    rx, ry, rw, rh = 46, 210, 210, 100
    out.append(S.node_objet(rx, ry, rw, rh, "Réservoir",
                            "un stock, un instant, un horizon"))
    rcx = rx + rw
    rcy = ry + rh/2

    # Trois métriques dérivées à droite (empilées, sans lien entre elles)
    mx, mw, mh = 560, 400, 96
    mets = [
        (96,  "Stock accessible", "quantité mobilisable \u2014 ex. phosphates solubles"),
        (212, "Flux accessible", "quantité transférable \u2014 ex. circulation hydrothermale"),
        (328, "Variation contrefactuelle de l'accessibilité",
              "part libérée par une intervention \u2014 ex. après fusion ou hydratation"),
    ]
    for my, title, sub in mets:
        out.append(S.node_metrique(mx, my, mw, mh, title, sub))
        mcy = my + mh/2
        out.append(S.edge_lecture(f'M{rcx},{rcy} C{rcx+90},{rcy} {mx-90},{mcy} {mx-4},{mcy}'))

    # accolade / axe : dérivation croissante, non une succession
    bx = mx + mw + 22
    out.append(f'<path d="M{bx},{96} C{bx+14},{96} {bx+14},{212} {bx+14},{212+96/2}" '
               f'fill="none" stroke="#b7bfc9" stroke-width="1.6"/>')
    out.append(f'<path d="M{bx},{328+96} C{bx+14},{328+96} {bx+14},{212+96} {bx+14},{212+96/2}" '
               f'fill="none" stroke="#b7bfc9" stroke-width="1.6"/>')
    out.append(f'<text x="{bx+26}" y="{262}" font-size="11.5" font-style="italic" '
               f'fill="#6a7481" transform="rotate(90 {bx+26} 262)" text-anchor="middle">'
               f'dérivation croissante, non une succession</text>')

    return "\n".join(out) + "\n</svg>\n"

if __name__ == "__main__":
    open("figure5.svg", "w").write(build())
    print("figure5.svg written")
