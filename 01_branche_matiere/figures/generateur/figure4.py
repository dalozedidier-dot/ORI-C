# -*- coding: utf-8 -*-
"""Figure 4 — Succession de la branche 2 (tri, différenciation, redistribution).
Grammaire corrigée : le 26Al et la provenance NC/CC sont des CONDITIONS latérales
(non des états matériels) ; la date d'accrétion ouvre une BIFURCATION précoce/tardive ;
enveloppes et intérieur COÉVOLUENT (double flèche) avec apports externes (condition)
et pertes ; « inventaire accessible » est une MÉTRIQUE dérivée (vert, pointillé) LUE
sur les réservoirs, non une étape traversée."""
import style as S

W, H = 1280, 780
NW, NH = 214, 60

def edges(cx, cy, w=NW, h=NH):
    return dict(l=(cx-w/2, cy), r=(cx+w/2, cy), t=(cx, cy-h/2), b=(cx, cy+h/2))

def build():
    out = [S.header(W, H), S.defs()]
    out.append(f'<text x="34" y="40" font-size="19" font-weight="700" fill="{S.INK}">'
               f'Branche 2 \u2014 différenciation, coévolution et inventaire accessible</text>')

    # ----- Positions (centres) -----
    P  = (150, 355)   # Planétésimaux
    AC = (430, 355)   # Accrétion + chauffage (mécanisme)
    EP = (712, 250)   # Accrétion précoce
    ET = (712, 460)   # Accrétion tardive
    RD = (992, 355)   # Réservoirs différenciés
    EM = (992, 632)   # Enveloppes mobiles
    IR = (600, 632)   # Interfaces réactives
    IA = (178, 632)   # Inventaire accessible (métrique)

    # ===== Liens (avant les noeuds) =====
    eP, eAC, eEP, eET, eRD = edges(*P), edges(*AC), edges(*EP), edges(*ET), edges(*RD)
    eEM, eIR = edges(*EM), edges(*IR)

    # Bande A : filiations
    out.append(S.edge_filiation(f'M{eP["r"][0]},{eP["r"][1]} L{eAC["l"][0]},{eAC["l"][1]}'))
    out.append(S.edge_filiation(f'M{eAC["r"][0]},{eAC["r"][1]-8} C{AC[0]+80},{EP[1]} {eEP["l"][0]-40},{eEP["l"][1]} {eEP["l"][0]},{eEP["l"][1]}'))
    out.append(S.edge_filiation(f'M{eAC["r"][0]},{eAC["r"][1]+8} C{AC[0]+80},{ET[1]} {eET["l"][0]-40},{eET["l"][1]} {eET["l"][0]},{eET["l"][1]}'))
    out.append(S.edge_filiation(f'M{eEP["r"][0]},{eEP["r"][1]} C{EP[0]+80},{EP[1]} {eRD["l"][0]-40},{eRD["l"][1]-8} {eRD["l"][0]},{eRD["l"][1]-8}'))
    out.append(S.edge_filiation(f'M{eET["r"][0]},{eET["r"][1]} C{ET[0]+80},{ET[1]} {eRD["l"][0]-40},{eRD["l"][1]+8} {eRD["l"][0]},{eRD["l"][1]+8}'))
    out.append(S.edge_label((AC[0]+EP[0])/2+18, 300, "précoce", S.L_FIL, size=10.5))
    out.append(S.edge_label((AC[0]+ET[0])/2+18, 430, "tardive", S.L_FIL, size=10.5))

    # A -> B : filiation descendante (décalée à gauche) + coévolution (à droite)
    out.append(S.edge_filiation(f'M{RD[0]-24},{eRD["b"][1]} L{EM[0]-24},{eEM["t"][1]}'))
    out.append(S.edge_coevolution(f'M{RD[0]+26},{eRD["b"][1]} L{EM[0]+26},{eEM["t"][1]}'))
    out.append(S.edge_label(RD[0]+120, (RD[1]+EM[1])/2-6, "coévolution :", S.L_COE, anchor="start", size=10.5))
    out.append(S.edge_label(RD[0]+120, (RD[1]+EM[1])/2+9, "dégazage, échanges", S.L_COE, anchor="start", size=10.5))
    out.append(S.edge_label(RD[0]+120, (RD[1]+EM[1])/2+24, "avec l'intérieur", S.L_COE, anchor="start", size=10.5))

    # Bande B : Enveloppes -> Interfaces (filiation gauche)
    out.append(S.edge_filiation(f'M{eEM["l"][0]},{eEM["l"][1]} L{eIR["r"][0]},{eIR["r"][1]}'))

    # Lectures (métrique) : Enveloppes et Interfaces -> Inventaire accessible
    eIA = edges(178, 632, 236, 96)
    out.append(S.edge_lecture(f'M{eIR["l"][0]},{eIR["l"][1]} L{eIA["r"][0]},{eIA["r"][1]}'))
    out.append(S.edge_lecture(f'M{eRD["l"][0]},{eRD["l"][1]+6} C{RD[0]-260},{RD[1]+40} {IA[0]+40},{IA[1]-140} {IA[0]},{632-48-2}'))

    # Condition : impacts / capture -> Enveloppes
    icx, icy, icw, ich = 884, 470, 216, 50
    out.append(S.node_condition(icx, icy, icw, ich, "Impacts, capture", "apports externes"))
    out.append(S.edge_condition(f'M{icx+icw/2},{icy+ich} C{icx+icw/2},{icy+ich+18} {EM[0]},{eEM["t"][1]-18} {EM[0]},{eEM["t"][1]-2}'))

    # Perte : échappement (matière qui quitte les enveloppes)
    out.append(S.edge_filiation(f'M{EM[0]},{eEM["b"][1]} L{EM[0]},{eEM["b"][1]+34}', w=1.8))
    out.append(S.edge_label(EM[0]+8, eEM["b"][1]+30, "échappement, pertes", S.L_FIL, anchor="start", size=10.5))

    # Conditions au-dessus de l'accrétion : provenance NC/CC + 26Al
    p1x, p1y, p1w, p1h = 236, 150, 220, 52
    out.append(S.node_condition(p1x, p1y, p1w, p1h, "Provenance NC / CC", "degré de mélange"))
    out.append(S.edge_condition(f'M{p1x+p1w/2},{p1y+p1h} C{p1x+p1w/2},{p1y+p1h+30} {AC[0]-20},{eAC["t"][1]-30} {AC[0]-20},{eAC["t"][1]-2}'))
    p2x, p2y, p2w, p2h = 486, 150, 236, 52
    out.append(S.node_condition(p2x, p2y, p2w, p2h, "\u00b2\u2076Al \u2014 chauffage radiogénique", "condition, non état matériel"))
    out.append(S.edge_condition(f'M{p2x+p2w/2-40},{p2y+p2h} C{p2x+p2w/2-40},{p2y+p2h+30} {AC[0]+20},{eAC["t"][1]-30} {AC[0]+20},{eAC["t"][1]-2}'))

    # ===== Noeuds =====
    out.append(S.node_objet(P[0]-NW/2, P[1]-NH/2, NW, NH, "Planétésimaux", "provenance et date"))
    out.append(S.node_mecanisme(AC[0]-NW/2, AC[1]-NH/2, NW, NH, "Accrétion + chauffage", "histoire thermique"))
    out.append(S.node_objet(EP[0]-NW/2, EP[1]-NH/2, NW, NH, "Accrétion précoce", "fusion, différenciation"))
    out.append(S.node_objet(ET[0]-NW/2, ET[1]-NH/2, NW, NH, "Accrétion tardive", "primitifs préservés"))
    out.append(S.node_objet(RD[0]-NW/2, RD[1]-NH/2, NW, NH, "Réservoirs différenciés", "noyau, manteau, croûte"))
    out.append(S.node_objet(EM[0]-NW/2, EM[1]-NH/2, NW, NH, "Enveloppes mobiles", "atmosphère + hydrosphère"))
    out.append(S.node_objet(IR[0]-NW/2, IR[1]-NH/2, NW, NH, "Interfaces réactives", "gradients, cycles"))
    out.append(S.node_metrique(60, 584, 236, 96, "Inventaire accessible",
                               "stock \u00b7 flux \u00b7 contrefactuel \u2014 mesure dérivée, non une étape"))

    return "\n".join(out) + "\n</svg>\n"

if __name__ == "__main__":
    open("figure4.svg", "w").write(build())
    print("figure4.svg written")
