# -*- coding: utf-8 -*-
"""Figure 2 — Nature réelle des relations historiques après reclassement.
Comptes vérifiés depuis reclassement_relations_v18.csv : 23/13/5/3/2/1 = 47."""
import style as S

W, H = 920, 430
X0 = 288          # départ des barres
BARMAX = 560      # largeur pour la valeur max (23)
CONTRAINTE = "#a8792e"  # teinte propre à la contrainte d'inventaire

ROWS = [
    ("Conditions d'ouverture", 23, S.L_CON),
    ("Filiations matérielles", 13, S.L_FIL),
    ("Transformations environnementales", 5, S.L_ENV),
    ("Dépendances non généalogiques", 3, S.L_DEP),
    ("Contraintes d'inventaire", 2, CONTRAINTE),
    ("Transmission de trace historique", 1, S.L_TRA),
]

def build():
    out = [S.header(W, H), S.defs()]
    out.append(f'<text x="34" y="42" font-size="19" font-weight="700" fill="{S.INK}">'
               f'Nature réelle des relations après reclassement</text>')
    out.append(f'<text x="34" y="63" font-size="12.5" fill="#5a6b7a">'
               f'La plupart des liens décrivaient un contexte ou une condition, non un transfert de matière '
               f'\u2014 47 relations</text>')

    vmax = max(v for _, v, _ in ROWS)
    scale = BARMAX / vmax
    y = 108
    rh = 50
    bh = 30
    for label, val, color in ROWS:
        out.append(f'<text x="{X0-16}" y="{y+bh/2+4:.0f}" text-anchor="end" '
                   f'font-size="13" fill="{S.INK}">{label}</text>')
        bw = val * scale
        out.append(f'<rect x="{X0}" y="{y}" width="{bw:.1f}" height="{bh}" rx="4" '
                   f'fill="{color}" opacity="0.9"/>')
        out.append(f'<text x="{X0+bw+10:.1f}" y="{y+bh/2+5:.0f}" font-size="14" '
                   f'font-weight="700" fill="{S.INK}">{val}</text>')
        y += rh

    # axe de base léger
    out.append(f'<line x1="{X0}" y1="98" x2="{X0}" y2="{y-rh+bh+8}" '
               f'stroke="#cbd3dc" stroke-width="1"/>')
    return "\n".join(out) + "\n</svg>\n"

if __name__ == "__main__":
    open("figure2.svg", "w").write(build())
    print("figure2.svg written")
