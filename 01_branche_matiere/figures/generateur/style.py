# -*- coding: utf-8 -*-
"""
Grammaire graphique partagée pour les figures ORI-C (branches 1 et 2).

Quatre natures de noeuds :
    objet      -> objet matériel / architecture      (bleu ardoise, plein)
    mecanisme  -> mécanisme / transformation         (sable, coins biseautés)
    condition  -> condition d'ouverture              (ambre, contour tireté)
    metrique   -> métrique dérivée                   (vert, contour pointillé)

Sept natures de liens :
    filiation   -> transmet des constituants          (plein, tête pleine, ardoise)
    condition   -> rend possible, sans filiation       (tireté latéral, ambre)
    transfo_env -> modifie le milieu                   (plein, sarcelle)
    lecture     -> lecture / dérivation d'un réservoir (pointillé, vert)
    dependance  -> dépendance non généalogique         (tireté long, gris, sans tête)
    trace       -> transmission de trace / provenance  (fin, violet, losange)
    coevolution -> rétroaction / coévolution           (double flèche, terre cuite)
"""

FONT = "'Liberation Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"

# ---- Palette ---------------------------------------------------------------
INK      = "#23303e"
PAGE     = "#ffffff"

OBJET    = dict(fill="#eaf0f7", stroke="#33556f", text="#22303f", sub="#4b6076")
MECAN    = dict(fill="#f4ecdd", stroke="#9a7736", text="#5a4620", sub="#7c6534")
CONDIT   = dict(fill="#fcf3e1", stroke="#c7922f", text="#7c581a", sub="#9a7430")
METRIQ   = dict(fill="#e9f3ec", stroke="#3d7c54", text="#234b31", sub="#3d6b4b")
RESERV   = dict(fill="#eef2f7", stroke="#33556f", text="#22303f", sub="#4b6076")  # variante objet

L_FIL    = "#33556f"   # filiation matérielle
L_CON    = "#c7922f"   # condition d'ouverture
L_ENV    = "#2e7d74"   # transformation environnementale
L_LEC    = "#3d7c54"   # lecture / dérivation
L_DEP    = "#8892a0"   # dépendance non généalogique
L_TRA    = "#7e5aa6"   # transmission de trace
L_COE    = "#b0533e"   # rétroaction / coévolution


def header(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">\n'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="{PAGE}"/>\n')


def defs():
    return f'''<defs>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="1.4" stdDeviation="1.8" flood-color="#1c2836" flood-opacity="0.16"/>
  </filter>
  <marker id="mFil" markerWidth="11" markerHeight="11" refX="8.2" refY="4" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M0.5,0.6 L8.6,4 L0.5,7.4 Z" fill="{L_FIL}"/>
  </marker>
  <marker id="mCon" markerWidth="12" markerHeight="12" refX="8.4" refY="4.2" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M1,1 L8.8,4.2 L1,7.4" fill="none" stroke="{L_CON}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="mEnv" markerWidth="11" markerHeight="11" refX="8.2" refY="4" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M0.5,0.6 L8.6,4 L0.5,7.4 Z" fill="{L_ENV}"/>
  </marker>
  <marker id="mLec" markerWidth="12" markerHeight="12" refX="8.4" refY="4.2" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M1,1 L8.8,4.2 L1,7.4" fill="none" stroke="{L_LEC}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <marker id="mCoeA" markerWidth="11" markerHeight="11" refX="8.2" refY="4" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M0.5,0.6 L8.6,4 L0.5,7.4 Z" fill="{L_COE}"/>
  </marker>
  <marker id="mCoeB" markerWidth="11" markerHeight="11" refX="2.6" refY="4" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M8.6,0.6 L0.5,4 L8.6,7.4 Z" fill="{L_COE}"/>
  </marker>
  <marker id="mTra" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto" markerUnits="userSpaceOnUse">
    <path d="M4.5,0.8 L8.2,4.5 L4.5,8.2 L0.8,4.5 Z" fill="{L_TRA}"/>
  </marker>
</defs>
'''


def _wrap(text, maxlen):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= maxlen:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _cap(width, fontsize, pad=18):
    """Nombre approximatif de caractères tenant dans (width - pad) à fontsize."""
    return max(6, int((width - pad) / (fontsize * 0.54)))


def _box(x, y, w, h, pal, title, sub, shape="round", dash=None, dot=None):
    cx = x + w / 2
    stroke_extra = ""
    if dash:
        stroke_extra = f' stroke-dasharray="{dash}"'
    if dot:
        stroke_extra = f' stroke-dasharray="{dot}"'
    if shape == "notch":
        c = 9
        d = (f'M{x+c},{y} L{x+w-c},{y} L{x+w},{y+c} L{x+w},{y+h-c} '
             f'L{x+w-c},{y+h} L{x+c},{y+h} L{x},{y+h-c} L{x},{y+c} Z')
        node = (f'<path d="{d}" fill="{pal["fill"]}" stroke="{pal["stroke"]}" '
                f'stroke-width="2"{stroke_extra} filter="url(#soft)"/>')
    else:
        rx = 11
        node = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                f'fill="{pal["fill"]}" stroke="{pal["stroke"]}" stroke-width="2"'
                f'{stroke_extra} filter="url(#soft)"/>')
    # texte
    TS, SS, LH, SH = 14.5, 11, 16, 13
    tlines = _wrap(title, _cap(w, TS))
    parts = [node]
    n_sub = len(_wrap(sub, _cap(w, SS))) if sub else 0
    block_h = len(tlines) * LH + (n_sub * SH + 4 if sub else 0)
    ty = y + (h - block_h) / 2 + TS - 2
    for ln in tlines:
        parts.append(f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" '
                     f'font-size="{TS}" font-weight="600" fill="{pal["text"]}">{ln}</text>')
        ty += LH
    if sub:
        ty += 2
        for sln in _wrap(sub, _cap(w, SS)):
            parts.append(f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" '
                         f'font-size="{SS}" fill="{pal["sub"]}">{sln}</text>')
            ty += SH
    return "\n".join(parts)


def node_objet(x, y, w, h, title, sub=""):
    return _box(x, y, w, h, OBJET, title, sub, shape="round")

def node_reservoir(x, y, w, h, title, sub=""):
    return _box(x, y, w, h, OBJET, title, sub, shape="round")

def node_mecanisme(x, y, w, h, title, sub=""):
    return _box(x, y, w, h, MECAN, title, sub, shape="notch")

def node_condition(x, y, w, h, title, sub=""):
    return _box(x, y, w, h, CONDIT, title, sub, shape="round", dash="6 4")

def node_metrique(x, y, w, h, title, sub=""):
    return _box(x, y, w, h, METRIQ, title, sub, shape="round", dot="2 4")


# ---- Liens -----------------------------------------------------------------
def _path(d, color, width, marker_end="", marker_start="", dash="", cls=""):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    me = f' marker-end="url(#{marker_end})"' if marker_end else ""
    ms = f' marker-start="url(#{marker_start})"' if marker_start else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round"{da}{me}{ms}/>')

def edge_filiation(d, w=2.4):
    return _path(d, L_FIL, w, marker_end="mFil")

def edge_condition(d, w=1.8):
    return _path(d, L_CON, w, marker_end="mCon", dash="6 4")

def edge_transfo_env(d, w=2.2):
    return _path(d, L_ENV, w, marker_end="mEnv")

def edge_lecture(d, w=1.7):
    return _path(d, L_LEC, w, marker_end="mLec", dash="1.5 4")

def edge_dependance(d, w=1.6):
    return _path(d, L_DEP, w, dash="2 4")

def edge_trace(d, w=1.5):
    return _path(d, L_TRA, w, marker_end="mTra")

def edge_coevolution(d, w=2.2):
    return _path(d, L_COE, w, marker_end="mCoeA", marker_start="mCoeB")


def edge_label(x, y, text, color, anchor="middle", size=11, italic=True):
    it = ' font-style="italic"' if italic else ""
    # halo blanc pour lisibilité au-dessus des traits
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}"'
            f'{it} fill="{color}" stroke="{PAGE}" stroke-width="3.2" '
            f'paint-order="stroke" stroke-linejoin="round">{text}</text>')
