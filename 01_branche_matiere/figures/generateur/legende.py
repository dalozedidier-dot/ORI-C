# -*- coding: utf-8 -*-
"""Panneau de légende : 4 natures de noeuds, 7 natures de liens."""
import style as S

W, H = 1000, 470

def sample_line(x1, y, x2, fn):
    return fn(f'M{x1},{y} L{x2},{y}')

def build():
    out = [S.header(W, H), S.defs()]
    out.append(f'<text x="34" y="46" font-size="21" font-weight="700" fill="{S.INK}">'
               f'Grammaire des figures</text>')
    out.append(f'<text x="34" y="70" font-size="13" fill="#5a6b7a">'
               f'Quatre natures de noeuds \u00b7 sept natures de liens</text>')
    out.append(f'<line x1="34" y1="86" x2="{W-34}" y2="86" stroke="#dfe5ec" stroke-width="1.5"/>')

    # ---- Colonne noeuds ----
    nx = 34
    out.append(f'<text x="{nx}" y="118" font-size="14" font-weight="700" fill="{S.INK}">NOEUDS</text>')
    ny = 134
    bw, bh = 250, 52
    out.append(S.node_objet(nx, ny, bw, bh, "Objet matériel", "architecture, réservoir, interface"))
    out.append(S.node_mecanisme(nx, ny+72, bw, bh, "Mécanisme", "transformation, transport, tri"))
    out.append(S.node_condition(nx, ny+144, bw, bh, "Condition d'ouverture", "rend possible, sans transfert"))
    out.append(S.node_metrique(nx, ny+216, bw, bh, "Métrique dérivée", "mesure lue sur un réservoir"))

    # ---- Colonne liens ----
    lx = 330
    x1, x2 = lx, lx + 92
    tx = lx + 108
    out.append(f'<text x="{lx}" y="118" font-size="14" font-weight="700" fill="{S.INK}">LIENS</text>')
    rows = [
        (S.edge_filiation,   "Filiation matérielle", "transmet des constituants"),
        (S.edge_condition,   "Condition d'ouverture", "rend une transition possible"),
        (S.edge_transfo_env, "Transformation environnementale", "modifie le milieu"),
        (S.edge_lecture,     "Lecture / dérivation", "d'un réservoir vers une mesure"),
        (S.edge_dependance,  "Dépendance non généalogique", "sans transfert de matière"),
        (S.edge_trace,       "Transmission de trace", "signature de provenance"),
        (S.edge_coevolution, "Rétroaction / coévolution", "entre réservoirs"),
    ]
    y = 150
    for fn, name, desc in rows:
        out.append(sample_line(x1, y, x2, fn))
        out.append(f'<text x="{tx}" y="{y-2}" font-size="13.5" font-weight="600" fill="{S.INK}">{name}</text>')
        out.append(f'<text x="{tx}" y="{y+14}" font-size="11.5" fill="#5a6b7a">{desc}</text>')
        y += 45

    return "\n".join(out) + "\n</svg>\n"

if __name__ == "__main__":
    open("legende.svg", "w").write(build())
    print("legende.svg written")
