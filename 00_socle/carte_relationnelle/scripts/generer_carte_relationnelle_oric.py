"""Génère une carte relationnelle ORI-C prudente et son registre autonome."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import html
import textwrap

import fitz
import networkx as nx
import pandas as pd
from graphviz import Digraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "resultats"
NODES_FILE = DATA / "noeuds_poc.csv"
RELATIONS_FILE = DATA / "relations_oric_47_provisoires.csv"
EXOPLANETS_FILE = DATA / "cas_exoplanetes.csv"

REL = {
    "ENBL": ("rend possible", "#2F6B45", "solid"),
    "MATR": ("fournit les constituants", "#A76523", "solid"),
    "ENVR": ("modifie l'environnement", "#2F6F94", "solid"),
    "STAB": ("stabilise", "#725B8C", "solid"),
    "CATL": ("catalyse", "#8A6D2F", "solid"),
    "CNST": ("contraint", "#666666", "dashed"),
    "CONT": ("contribue ou favorise", "#7A5E99", "dashed"),
    "DEPG": ("dépendance fonctionnelle générale", "#596B7A", "dotted"),
    "INCO": ("incorporation ou trace", "#8B6F47", "dotted"),
    "DESC": ("ascendance générale", "#555555", "dotted"),
    "FEED": ("rétroaction", "#A52A2A", "bold"),
}
EXPECTED_COUNTS = {
    "ENBL": 19,
    "MATR": 13,
    "ENVR": 4,
    "STAB": 2,
    "CATL": 1,
    "CNST": 2,
    "CONT": 1,
    "DEPG": 1,
    "INCO": 1,
    "DESC": 2,
    "FEED": 1,
}
REGIME = {
    1: ("R1", "Physique fondamentale", "#EAF0F5"),
    2: ("R2", "Atomes et étoiles", "#F5EFE7"),
    3: ("R3", "Molécules", "#EAF4EC"),
    4: ("R4", "Solides cosmiques", "#F5ECEA"),
    5: ("R5", "Architectures planétaires", "#F0EDF5"),
    6: ("R6", "Diversification minérale", "#F4F0EA"),
    7: ("R7", "Voies prébiotiques", "#F6EDF3"),
    8: ("R8", "Vivant", "#EEEEEE"),
}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def regime_from_id(tid: str) -> int:
    return (int(tid.split("-")[1]) - 1) // 5 + 1


def wrapped_html(text: str, width: int = 29, max_lines: int = 3) -> str:
    lines = textwrap.wrap(str(text).strip(), width=width, break_long_words=False)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "..."
    return "<BR/>".join(html.escape(line) for line in lines)


def load_and_validate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    nodes = pd.read_csv(NODES_FILE, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    edges = pd.read_csv(RELATIONS_FILE, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    exoplanets = pd.read_csv(EXOPLANETS_FILE, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    nodes.columns = [c.strip().lower() for c in nodes.columns]
    edges.columns = [c.strip().lower() for c in edges.columns]
    exoplanets.columns = [c.strip().lower() for c in exoplanets.columns]

    required_nodes = {"id", "transition", "regime_num", "regime_nom"}
    required_edges = {
        "source", "target", "relation", "portee_du_lien", "niveau_preuve", "mode_preuve",
        "justification", "limite_interpretative", "reference_cle",
    }
    if not required_nodes.issubset(nodes.columns):
        raise ValueError(f"Colonnes de noeuds manquantes : {sorted(required_nodes - set(nodes.columns))}")
    if not required_edges.issubset(edges.columns):
        raise ValueError(f"Colonnes de liens manquantes : {sorted(required_edges - set(edges.columns))}")
    required_exo = {"cas", "observation", "statut", "mode_preuve", "limite", "valeur_ori_c", "reference"}
    if not required_exo.issubset(exoplanets.columns):
        raise ValueError(f"Colonnes exoplanétaires manquantes : {sorted(required_exo - set(exoplanets.columns))}")

    nodes["id"] = nodes["id"].str.strip()
    for col in ["source", "target", "relation"]:
        edges[col] = edges[col].str.strip()
    edges["relation"] = edges["relation"].str.upper()

    expected_ids = [f"TR-{i:03d}" for i in range(1, 41)]
    if nodes["id"].tolist() != expected_ids:
        raise ValueError("Les identifiants ne suivent pas strictement TR-001 à TR-040.")
    if len(nodes) != 40 or len(edges) != 47:
        raise ValueError(f"40 transitions et 47 liens attendus, trouvé : {len(nodes)} et {len(edges)}.")
    if edges.duplicated(["source", "target", "relation"]).any():
        raise ValueError("Le CSV contient au moins un lien strictement dupliqué.")
    known_nodes = set(nodes["id"])
    endpoints = set(edges["source"]) | set(edges["target"])
    unknown = endpoints - known_nodes
    if unknown:
        raise ValueError(f"Extrémités inconnues : {sorted(unknown)}")
    unknown_rel = sorted(set(edges["relation"]) - set(REL))
    if unknown_rel:
        raise ValueError(f"Codes inconnus : {unknown_rel}")
    actual = {code: int((edges["relation"] == code).sum()) for code in REL}
    if actual != EXPECTED_COUNTS:
        raise ValueError(f"Répartition inattendue : {actual}")
    allowed_status = {"Établi", "Fortement inféré", "Plausible", "Hypothétique"}
    if set(edges["niveau_preuve"]) - allowed_status:
        raise ValueError(f"Statuts non normalisés : {sorted(set(edges["niveau_preuve"]) - allowed_status)}")
    for col in ["portee_du_lien", "niveau_preuve", "mode_preuve", "justification", "limite_interpretative"]:
        if (edges[col].str.strip() == "").any():
            raise ValueError(f"Chaque lien doit renseigner {col}.")
    if len(exoplanets) != 3:
        raise ValueError(f"Trois cas exoplanétaires attendus, {len(exoplanets)} trouvés.")
    return nodes, edges, exoplanets


def build_graph(nodes: pd.DataFrame, edges: pd.DataFrame, include_feed: bool = True) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes["id"])
    for row in edges.itertuples(index=False):
        if include_feed or row.relation != "FEED":
            graph.add_edge(row.source, row.target, relation=row.relation)
    return graph


def write_adjacency(nodes: pd.DataFrame, edges: pd.DataFrame) -> Path:
    ids = nodes["id"].tolist()
    matrix = pd.DataFrame("", index=ids, columns=ids)
    for row in edges.itertuples(index=False):
        old = matrix.loc[row.source, row.target]
        matrix.loc[row.source, row.target] = row.relation if not old else old + "|" + row.relation
    matrix.index.name = "source\\target"
    out = RESULTS / "matrice_relations_oric_47.csv"
    matrix.to_csv(out, sep=";", encoding="utf-8-sig", lineterminator="\n")
    return out


def write_audit(nodes: pd.DataFrame, edges: pd.DataFrame, adjacency: Path) -> Path:
    graph = build_graph(nodes, edges, include_feed=True)
    dag = build_graph(nodes, edges, include_feed=False)
    cycles_all = list(nx.simple_cycles(graph))
    cycles_non_feed = list(nx.simple_cycles(dag))
    weak_components = list(nx.weakly_connected_components(graph))
    counts = edges["relation"].value_counts().to_dict()
    referenced = int((edges["reference_cle"].str.strip() != "").sum())
    noncausal = int(edges["relation"].isin(["INCO", "DESC", "DEPG"]).sum())
    contributive = int((edges["relation"] == "CONT").sum())

    lines = [
        "AUDIT DE LA CARTE RELATIONNELLE ORI-C",
        "=====================================",
        f"Transitions : {len(nodes)}",
        f"Liens typés : {len(edges)}",
        f"Composantes faiblement connexes : {len(weak_components)}",
        f"Cycles hors FEED : {len(cycles_non_feed)}",
        f"Cycles avec FEED : {len(cycles_all)}",
        f"Liens explicitement non causaux : {noncausal}",
        f"Liens contributifs non suffisants : {contributive}",
        f"Liens avec référence clé jointe : {referenced}/{len(edges)}",
        "",
        "Répartition des codes :",
    ]
    for code in REL:
        lines.append(f"  {code}: {counts.get(code, 0)}")
    lines.extend(["", "Statuts scientifiques normalisés :"])
    for level in ["Établi", "Fortement inféré", "Plausible", "Hypothétique"]:
        lines.append(f"  {level}: {int((edges["niveau_preuve"] == level).sum())}")
    lines.extend(["", "Modes de preuve principaux :"])
    for mode, count in edges["mode_preuve"].value_counts().items():
        lines.append(f"  {mode}: {count}")
    lines.extend([
        "",
        "Empreintes SHA-256 :",
        f"  {NODES_FILE.name}: {file_sha256(NODES_FILE)}",
        f"  {RELATIONS_FILE.name}: {file_sha256(RELATIONS_FILE)}",
        f"  {adjacency.name}: {file_sha256(adjacency)}",
        "",
        "Statut : cohérence structurelle vérifiée uniquement.",
        "La carte mélange volontairement plusieurs classes de liens historiques, mais les liens",
        "d'incorporation, d'ascendance et de dépendance fonctionnelle générale sont déclarés",
        "non causaux historiquement. Le niveau de preuve est un",
        "classement interne prudent et ne remplace pas une revue bibliographique relation par relation.",
        "Les cas TRAPPIST-1d, TRAPPIST-1e et 55 Cancri e sont traités comme cas d’étude,",
        "sans être ajoutés aux transitions fondamentales de la carte.",
    ])
    out = RESULTS / "audit_carte_relationnelle_oric_47.txt"
    # newline="\n" : l'empreinte de l'audit ne doit pas dépendre du système.
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return out


def draw_graph(nodes: pd.DataFrame, edges: pd.DataFrame) -> list[Path]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    dot = Digraph("ORI_C_47", engine="dot")
    dot.attr(
        rankdir="TB", newrank="true", compound="true", splines="spline",
        overlap="false", concentrate="false", outputorder="edgesfirst",
        nodesep="0.23", ranksep="0.68 equally", pad="0.18", margin="0.04",
        bgcolor="white", size="15.8,22.7!", ratio="compress", dpi="240",
        labelloc="t",
        label="Carte relationnelle de travail ORI-C\n40 transitions, 47 liens typés - causalité, dépendances et contexte distingués",
        fontsize="18", fontname="DejaVu Sans",
    )
    dot.attr(
        "node", shape="box", style="rounded,filled", fontname="DejaVu Sans",
        fontsize="8.4", color="#43596A", penwidth="0.9", margin="0.08,0.05",
        width="2.18", height="0.70", fixedsize="true",
    )
    dot.attr("edge", arrowsize="0.62", penwidth="1.15", fontname="DejaVu Sans", fontsize="6.5")

    node_name = dict(zip(nodes["id"], nodes["transition"]))
    for r in range(1, 9):
        code, title, fill = REGIME[r]
        with dot.subgraph(name=f"cluster_R{r}") as cluster:
            cluster.attr(
                label=f"{code}  {title}", color="#9AA9B3", penwidth="0.8",
                style="rounded,filled", fillcolor=fill, fontsize="10.5",
                fontname="DejaVu Sans", labelloc="t", margin="12",
            )
            cluster.attr(rank="same")
            ids = [f"TR-{i:03d}" for i in range((r - 1) * 5 + 1, r * 5 + 1)]
            for tid in ids:
                label = f'<{html.escape(tid)}<BR/><FONT POINT-SIZE="7.4">{wrapped_html(node_name[tid])}</FONT>>'
                cluster.node(tid, label=label, fillcolor=fill, tooltip=node_name[tid])
            for a, b in zip(ids, ids[1:]):
                cluster.edge(a, b, style="invis", weight="80")

    representatives = [f"TR-{(r - 1) * 5 + 1:03d}" for r in range(1, 9)]
    for a, b in zip(representatives, representatives[1:]):
        dot.edge(a, b, style="invis", weight="1200", minlen="2")

    pair_totals = edges.groupby(["source", "target"]).size().to_dict()
    for row in edges.itertuples(index=False):
        label, color, style = REL[row.relation]
        source_regime = regime_from_id(row.source)
        target_regime = regime_from_id(row.target)
        attrs = {
            "color": color,
            "style": style,
            "constraint": "true" if target_regime > source_regime and row.relation != "FEED" else "false",
            "tooltip": f"{row.relation}: {label} - {row.justification}",
        }
        if target_regime > source_regime:
            attrs["minlen"] = str(max(1, target_regime - source_regime))
        if pair_totals[(row.source, row.target)] > 1:
            attrs["label"] = row.relation
            attrs["fontcolor"] = color
            attrs["fontsize"] = "6.2"
        if row.relation == "FEED":
            attrs["penwidth"] = "2.0"
            attrs["constraint"] = "false"
        dot.edge(row.source, row.target, **attrs)

    cells = []
    for code, (label, color, _style) in REL.items():
        cells.append(f'<TD BORDER="0" CELLPADDING="5"><FONT COLOR="{color}"><B>{code}</B>  {html.escape(label)}</FONT></TD>')
    split = 5
    legend_html = (
        '<<TABLE BORDER="1" COLOR="#B5BEC5" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2">'
        '<TR><TD COLSPAN="5"><B>Codes de liens</B></TD></TR>'
        f'<TR>{"".join(cells[:split])}</TR><TR>{"".join(cells[split:])}</TR>'
        '<TR><TD COLSPAN="5"><FONT POINT-SIZE="6.5">INCO, DESC et DEPG sont contextuels et non causaux historiquement; CONT indique une contribution non suffisante.</FONT></TD></TR>'
        '</TABLE>>'
    )
    dot.node("LEGEND", label=legend_html, shape="plain", style="", fillcolor="white", color="white", fontname="DejaVu Sans", fontsize="8.2", fixedsize="false", width="0", height="0")
    dot.edge("TR-036", "LEGEND", style="invis", weight="1500", minlen="2")

    source = RESULTS / "carte_relationnelle_oric_47.dot"
    source.write_text(dot.source, encoding="utf-8", newline="\n")
    outputs = [source]
    stem = RESULTS / "carte_relationnelle_oric_47"
    for fmt in ("pdf", "png", "svg"):
        dot.format = fmt
        outputs.append(Path(dot.render(filename=str(stem), cleanup=True)))
    return outputs


def register_fonts() -> str:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("ORIRegular", str(path)))
            return "ORIRegular"
    return "Helvetica"


def build_register_pdf(nodes: pd.DataFrame, edges: pd.DataFrame, exoplanets: pd.DataFrame) -> Path:
    font = register_fonts()
    out = RESULTS / "registre_relations_oric_47.pdf"
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName=font, fontSize=16, leading=19, alignment=TA_CENTER, spaceAfter=8)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName=font, fontSize=7.2, leading=9, alignment=TA_LEFT)
    small = ParagraphStyle("small", parent=body, fontSize=6.3, leading=7.7)
    head = ParagraphStyle("head", parent=small, fontSize=6.5, leading=8, alignment=TA_CENTER, textColor=colors.white)

    doc = SimpleDocTemplate(
        str(out), pagesize=landscape(A4), leftMargin=10*mm, rightMargin=10*mm,
        topMargin=12*mm, bottomMargin=12*mm, title="Registre des relations ORI-C",
    )
    story = [
        Paragraph("Comment lire la carte relationnelle ORI-C", title),
        Paragraph(
            "Cette carte est un outil de travail interne. Une flèche représente un lien typé, mais pas nécessairement une causalité directe. "
            "Le mot <b>établi</b> qualifie la solidité d'une dépendance ou d'un mécanisme général; il ne signifie pas que la séquence historique exacte a été observée.",
            body,
        ),
        Spacer(1, 3*mm),
        Paragraph("Statuts scientifiques", ParagraphStyle("subhead", parent=body, fontSize=10, leading=12, spaceAfter=3)),
        Paragraph(
            "<b>Établi</b> : relation largement soutenue par des observations, des expériences ou un mécanisme robuste. "
            "<b>Fortement inféré</b> : relation historique soutenue par plusieurs archives, reconstructions ou simulations concordantes, sans observation directe de l’événement. "
            "<b>Plausible</b> : relation compatible avec les connaissances, mais indirecte, partielle ou dépendante de conditions supplémentaires. "
            "<b>Hypothétique</b> : trajectoire ou contribution encore ouverte, sans preuve discriminante.",
            body,
        ),
        Spacer(1, 3*mm),
        Paragraph("Modes de preuve", ParagraphStyle("modes", parent=body, fontSize=10, leading=12, spaceAfter=3)),
        Paragraph(
            "<b>Observation</b> : signal, objet ou relation accessible par mesure. "
            "<b>Reconstruction</b> : événement passé déduit d’archives, d’isotopes, de phylogénies ou de modèles inverses. "
            "<b>Simulation</b> : comportement obtenu dans un modèle numérique sous hypothèses explicites. "
            "<b>Expérimentation</b> : mécanisme reproduit en laboratoire. "
            "<b>Hypothèse</b> : scénario compatible mais non discriminé. Une ligne peut combiner plusieurs modes.",
            body,
        ),
        Spacer(1, 3*mm),
        Paragraph("Trois codes contextuels à ne pas lire comme des causes", ParagraphStyle("subhead2", parent=body, fontSize=10, leading=12, spaceAfter=3)),
        Paragraph(
            "<b>INCO</b> : un élément plus ancien peut être incorporé, remanié ou conservé comme trace dans un objet ultérieur; il ne le produit pas. "
            "<b>DESC</b> : une innovation tardive apparaît dans des lignées descendantes; l'ancêtre n'est pas supposé posséder ni causer cette innovation. "
            "<b>DEPG</b> : une fonction tardive suppose une machinerie générale déjà présente, par exemple le code et la traduction; cette machinerie ne cause pas directement l'innovation particulière.",
            body,
        ),
        Spacer(1, 3*mm),
        Paragraph(
            "Les liens prébiotiques décrivent des mécanismes candidats et non une succession historique démontrée. "
            "Les références indiquées sont des points d’entrée bibliographiques, pas une revue systématique exhaustive. "
            "Le registre reste un document de travail et n’a pas été soumis à une relecture par les pairs.",
            body,
        ),
        PageBreak(),
        Paragraph("Cas d’étude : exoplanètes et contingence historique", title),
        Paragraph(
            "Les exoplanètes servent ici à comparer des domaines de possibilités et à éliminer certaines trajectoires. "
            "Elles ne permettent généralement pas de reconstruire une histoire unique. La divergence de plusieurs planètes d’un même système ne constitue pas une polygenèse : ce terme est réservé à l’apparition indépendante d’une même organisation ou fonction.",
            body,
        ),
        Spacer(1, 4*mm),
        PageBreak(),
        Paragraph("Registre des 47 liens typés", title),
        Paragraph(
            "Chaque ligne précise la portée du lien, son statut, sa justification, sa limite d'interprétation et la référence clé actuellement disponible.",
            body,
        ),
        Spacer(1, 5*mm),
    ]
    exo_header = [
        Paragraph("Cas", head), Paragraph("Observation", head), Paragraph("Statut", head),
        Paragraph("Mode de preuve", head), Paragraph("Limite", head),
        Paragraph("Valeur pour ORI-C", head), Paragraph("Référence", head),
    ]
    exo_rows = [exo_header]
    for row in exoplanets.itertuples(index=False):
        exo_rows.append([
            Paragraph(html.escape(row.cas), small),
            Paragraph(html.escape(row.observation), small),
            Paragraph(html.escape(row.statut), small),
            Paragraph(html.escape(row.mode_preuve), small),
            Paragraph(html.escape(row.limite), small),
            Paragraph(html.escape(row.valeur_ori_c), small),
            Paragraph(html.escape(row.reference), small),
        ])
    exo_table = Table(exo_rows, repeatRows=1, colWidths=[24*mm, 52*mm, 26*mm, 29*mm, 55*mm, 48*mm, 43*mm], hAlign="CENTER")
    exo_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#43596A")),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#B7C0C7")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F7F8")]),
    ]))
    # Place the exoplanet table after its introduction and before the page break
    # leading to the 47-link register. The first PageBreak closes the reading guide;
    # the second closes the exoplanet case-study page.
    page_breaks = [i for i, item in enumerate(story) if isinstance(item, PageBreak)]
    if len(page_breaks) < 2:
        raise RuntimeError("Structure inattendue du registre PDF : deux sauts de page sont requis.")
    register_break = page_breaks[1]
    story.insert(register_break, Spacer(1, 3*mm))
    story.insert(register_break + 1, exo_table)

    name = dict(zip(nodes["id"], nodes["transition"]))
    header = [
        Paragraph("N°", head), Paragraph("Lien", head), Paragraph("Code et portée", head),
        Paragraph("Statut", head), Paragraph("Mode de preuve", head), Paragraph("Justification", head),
        Paragraph("Limite d'interprétation", head), Paragraph("Référence clé", head),
    ]
    rows = [header]
    for i, row in enumerate(edges.itertuples(index=False), start=1):
        link = f"<b>{row.source}</b> {html.escape(name[row.source])}<br/>→ <b>{row.target}</b> {html.escape(name[row.target])}"
        rows.append([
            Paragraph(str(i), small),
            Paragraph(link, small),
            Paragraph(f"<b>{row.relation}</b><br/>{html.escape(row.portee_du_lien)}", small),
            Paragraph(html.escape(row.niveau_preuve), small),
            Paragraph(html.escape(row.mode_preuve), small),
            Paragraph(html.escape(row.justification), small),
            Paragraph(html.escape(row.limite_interpretative), small),
            Paragraph(html.escape(row.reference_cle) if row.reference_cle else "Référence clé à joindre", small),
        ])
    widths = [7*mm, 40*mm, 25*mm, 19*mm, 25*mm, 55*mm, 48*mm, 48*mm]
    table = LongTable(rows, repeatRows=1, colWidths=widths, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#43596A")),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#B7C0C7")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F7F8")]),
    ]))
    story.append(table)

    def footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont(font, 7)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawCentredString(landscape(A4)[0]/2, 6*mm, f"ORI-C - carte de travail - page {doc_obj.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out


def merge_complete_pdf(graph_pdf: Path, register_pdf: Path) -> Path:
    out = RESULTS / "carte_relationnelle_oric_47_complete.pdf"
    merged = fitz.open()
    for source in [graph_pdf, register_pdf]:
        doc = fitz.open(source)
        merged.insert_pdf(doc)
        doc.close()
    merged.save(out)
    merged.close()
    return out


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    nodes, edges, exoplanets = load_and_validate()
    adjacency = write_adjacency(nodes, edges)
    audit = write_audit(nodes, edges, adjacency)
    graph_outputs = draw_graph(nodes, edges)
    graph_pdf = next(p for p in graph_outputs if p.suffix == ".pdf")
    register_pdf = build_register_pdf(nodes, edges, exoplanets)
    complete_pdf = merge_complete_pdf(graph_pdf, register_pdf)
    print("GENERATION REUSSIE")
    print(f"- transitions : {len(nodes)}")
    print(f"- liens : {len(edges)}")
    for path in [adjacency, audit, *graph_outputs, register_pdf, complete_pdf]:
        print(f"- {path}")


if __name__ == "__main__":
    main()
