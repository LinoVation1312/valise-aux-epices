import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- CONFIGURATION ---
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVER = "lino.conord@gmail.com"
EXCEL_FILE_PATH = "menu_actuel.xlsx"

st.set_page_config(
    page_title="La Valise aux Épices",
    page_icon="🥘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* Fond général */
    .stApp {
        background-color: #FDFAF5;
    }

    /* Masquer les éléments Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Titre principal */
    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #3B2A1A !important;
        text-align: center;
        font-size: 3rem !important;
        letter-spacing: 2px;
        font-weight: 600;
    }

    /* Sous-titres */
    h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #7A4F2E !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #E8C99A;
        padding-bottom: 6px;
        margin-top: 1.5rem !important;
    }

    /* Texte général */
    p, label, div {
        font-family: 'Lato', sans-serif !important;
        color: #3B2A1A;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border: 1.5px solid #D4A96A;
        border-radius: 8px;
        background-color: #FFFDF8;
        color: #3B2A1A;
        font-family: 'Lato', sans-serif;
    }
    .stTextInput > div > div > input:focus {
        border-color: #C47C2B;
        box-shadow: 0 0 0 2px rgba(196,124,43,0.2);
    }

    /* Selectbox */
    .stSelectbox > div > div {
        border: 1.5px solid #D4A96A;
        border-radius: 8px;
        background-color: #FFFDF8;
    }

    /* Checkboxes */
    .stCheckbox > label {
        font-family: 'Lato', sans-serif !important;
        font-size: 0.95rem;
        color: #3B2A1A;
    }

    /* Bouton principal */
    .stFormSubmitButton > button {
        background-color: #C47C2B !important;
        color: white !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2.5rem !important;
        width: 100%;
        transition: background-color 0.3s;
        letter-spacing: 1.5px;
    }
    .stFormSubmitButton > button:hover {
        background-color: #A5621E !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #C47C2B !important;
        color: #FFFFFF !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 3px 10px rgba(196,124,43,0.4) !important;
        transition: background-color 0.3s, box-shadow 0.3s !important;
    }
    .stDownloadButton > button:hover {
        background-color: #A5621E !important;
        box-shadow: 0 5px 15px rgba(196,124,43,0.5) !important;
    }
    .stDownloadButton > button p {
        color: #FFFFFF !important;
    }

    /* Radio */
    .stRadio > div {
        background-color: #FEF6E8;
        border-radius: 10px;
        padding: 12px 16px;
        border: 1.5px solid #E8C99A;
    }

    /* Cards de plats */
    .dish-card {
        background: white;
        border: 1.5px solid #E8C99A;
        border-radius: 12px;
        padding: 10px 14px;
        margin: 4px 0;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .dish-card:hover {
        border-color: #C47C2B;
        box-shadow: 0 2px 8px rgba(196,124,43,0.15);
    }

    /* Banner/header personnalisé */
    .banner {
        background: linear-gradient(135deg, #3B2A1A 0%, #7A4F2E 50%, #C47C2B 100%);
        border-radius: 16px;
        padding: 28px 20px 22px;
        text-align: center;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px rgba(59,42,26,0.25);
    }
    .banner h1 {
        color: #FEF6E8 !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 2.8rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        letter-spacing: 3px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .banner p {
        color: #E8C99A !important;
        font-family: 'Lato', sans-serif !important;
        font-size: 0.85rem !important;
        margin: 8px 0 0 !important;
        letter-spacing: 4px;
        text-transform: uppercase;
    }

    /* Séparateur élégant */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #E8C99A, transparent);
        margin: 20px 0;
        border: none;
    }

    /* Info box */
    .info-box {
        background: #FEF6E8;
        border-left: 4px solid #C47C2B;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
        font-family: 'Lato', sans-serif;
        color: #3B2A1A;
        font-size: 0.9rem;
    }

    /* Compteur de plats */
    .counter-badge {
        background: #C47C2B;
        color: white;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.85rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# --- FONCTIONS UTILITAIRES ---
def load_menu():
    if os.path.exists(EXCEL_FILE_PATH):
        return pd.read_excel(EXCEL_FILE_PATH, sheet_name=None)
    return None


def normalize_ingredient(name):
    """Normalise un nom d'ingrédient pour la déduplication (minuscules, sans accents, sans 's' final)."""
    import unicodedata
    name = str(name).strip().lower()
    # Suppression des accents
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    # Supprime le 's' final pour unifier singulier/pluriel
    if name.endswith('s') and len(name) > 3:
        name = name[:-1]
    return name


def calculate_groceries(menu_data, selected_dishes, num_guests):
    shopping_list = []
    ratio = num_guests / 4.0
    for dish in selected_dishes:
        df = menu_data[dish]
        for _, row in df.iterrows():
            shopping_list.append({
                "Plat": dish,
                "Ingrédient": row['Ingrédient'],
                "Quantité": row['Quantité'] * ratio,
                "Unité": row['Unité']
            })
    df_all = pd.DataFrame(shopping_list)

    # --- Déduplication par liste globale (toutes sections confondues) ---
    # On crée une clé de normalisation
    df_all['_key'] = df_all['Ingrédient'].apply(normalize_ingredient) + '__' + df_all['Unité'].astype(str).str.strip().str.lower()

    # Pour chaque clé, on garde le nom le plus fréquent (ou le premier)
    canonical_names = df_all.groupby('_key')['Ingrédient'].agg(lambda x: x.value_counts().index[0])
    df_all['Ingrédient'] = df_all['_key'].map(canonical_names)

    # Grouper par Plat + clé normalisée pour sommer les quantités dans chaque plat
    df_agg = (
        df_all.groupby(['Plat', '_key'], sort=False)
        .agg(Ingrédient=('Ingrédient', 'first'), Quantité=('Quantité', 'sum'), Unité=('Unité', 'first'))
        .reset_index()
        .drop(columns='_key')
    )
    # Restaurer l'ordre d'origine des plats
    df_agg['Plat'] = pd.Categorical(df_agg['Plat'], categories=selected_dishes, ordered=True)
    df_agg = df_agg.sort_values('Plat').reset_index(drop=True)

    return df_agg


def generate_pdf(shopping_df, name, firstname, address=None, num_guests=4, selected_dishes=None):
    """Génère un PDF élégant avec ReportLab."""
    pdf_filename = f"La_Valise_aux_Epices_{firstname}_{name}.pdf"

    # --- Palette : crème chaud / terracotta / or sable ---
    ENCRE       = colors.HexColor("#1C1208")   # titres foncés
    TERRACOTTA  = colors.HexColor("#B85C38")   # accents chauds
    TERRE       = colors.HexColor("#6B3D2E")   # secondaire
    OR          = colors.HexColor("#D4973A")   # dorure
    OR_PALE     = colors.HexColor("#EDD79A")   # fond léger doré
    SABLE       = colors.HexColor("#F5ECD7")   # fond crème
    PARCHEMIN   = colors.HexColor("#FBF6EC")   # fond très clair
    BLANC       = colors.white
    GRIS        = colors.HexColor("#888888")

    W = 17 * cm  # largeur utile

    doc = SimpleDocTemplate(
        pdf_filename, pagesize=A4,
        topMargin=1.8*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm
    )
    styles = getSampleStyleSheet()

    # ---- styles réutilisables ----
    def S(name, **kw):
        return ParagraphStyle(name, parent=styles['Normal'], **kw)

    sT  = S('sT',  fontSize=26, textColor=BLANC,      fontName='Times-Bold',    alignment=TA_CENTER, leading=32)
    sST = S('sST', fontSize=8,  textColor=OR_PALE,    fontName='Helvetica',     alignment=TA_CENTER, leading=13, charSpace=2)
    sCL = S('sCL', fontSize=8,  textColor=TERRACOTTA, fontName='Helvetica-Bold',leading=11)
    sCV = S('sCV', fontSize=11, textColor=ENCRE,      fontName='Times-Roman',   leading=15)
    sPT = S('sPT', fontSize=12, textColor=BLANC,      fontName='Times-Bold',    leading=16)
    sIL = S('sIL', fontSize=10, textColor=ENCRE,      fontName='Times-Roman',   leading=14)
    sQT = S('sQT', fontSize=10, textColor=TERRACOTTA, fontName='Helvetica-Bold',leading=14, alignment=TA_RIGHT)
    sRM = S('sRM', fontSize=8,  textColor=GRIS,       fontName='Helvetica-Oblique', alignment=TA_CENTER, leading=12)
    sSH = S('sSH', fontSize=11, textColor=BLANC,      fontName='Times-Bold',    leading=15, alignment=TA_CENTER)

    elements = []

    # ══════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════
    # Ligne décorative dorée très fine
    elements.append(Table([[""]], colWidths=[W], rowHeights=[3],
        style=TableStyle([('BACKGROUND',(0,0),(-1,-1), OR)])))

    # Titre principal sur fond encre
    elements.append(Table(
        [[Paragraph("La Valise aux Epices", sT)]],
        colWidths=[W],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), ENCRE),
            ('TOPPADDING',(0,0),(-1,-1), 22),
            ('BOTTOMPADDING',(0,0),(-1,-1), 16),
            ('LEFTPADDING',(0,0),(-1,-1), 10),
            ('RIGHTPADDING',(0,0),(-1,-1), 10),
        ])
    ))
    # Bandeau sous-titre terracotta
    elements.append(Table(
        [[Paragraph("LISTE DE COURSES", sST)]],
        colWidths=[W],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), TERRACOTTA),
            ('TOPPADDING',(0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ])
    ))
    # Ligne dorée fine
    elements.append(Table([[""]], colWidths=[W], rowHeights=[3],
        style=TableStyle([('BACKGROUND',(0,0),(-1,-1), OR)])))
    elements.append(Spacer(1, 0.5*cm))

    # ══════════════════════════════════════════
    # FICHE CLIENT
    # ══════════════════════════════════════════
    col1 = 10.5*cm; col2 = 6.5*cm
    client_rows = [
        [Paragraph("CLIENT", sCL),        Paragraph("COUVERTS", sCL)],
        [Paragraph(f"{firstname} {name}", sCV),
         Paragraph(f"{num_guests} personne{'s' if num_guests > 1 else ''}", sCV)],
    ]
    if address:
        client_rows += [
            [Paragraph("ADRESSE DE LIVRAISON", sCL), Paragraph("", sCL)],
            [Paragraph(address, sCV), Paragraph("", sCV)],
        ]
    ct = Table(client_rows, colWidths=[col1, col2])
    ct.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), PARCHEMIN),
        ('BOX',(0,0),(-1,-1), 1, OR_PALE),
        ('LINEBELOW',(0,1),(-1,1), 0.5, OR_PALE),
        ('TOPPADDING',(0,0),(-1,-1), 5), ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING',(0,0),(-1,-1), 12), ('RIGHTPADDING',(0,0),(-1,-1), 10),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    elements.append(ct)
    elements.append(Spacer(1, 0.35*cm))

    # Bandeau plats choisis
    if selected_dishes:
        plats_text = "  ·  ".join(selected_dishes)
        elements.append(Table(
            [[Paragraph(plats_text, S('sP', fontSize=8, textColor=TERRE,
                fontName='Helvetica-Oblique', alignment=TA_CENTER, leading=12))]],
            colWidths=[W],
            style=TableStyle([
                ('BACKGROUND',(0,0),(-1,-1), SABLE),
                ('TOPPADDING',(0,0),(-1,-1), 5), ('BOTTOMPADDING',(0,0),(-1,-1), 5),
                ('LINEABOVE',(0,0),(-1,0), 0.5, OR), ('LINEBELOW',(0,0),(-1,0), 0.5, OR),
                ('LEFTPADDING',(0,0),(-1,-1), 8), ('RIGHTPADDING',(0,0),(-1,-1), 8),
            ])
        ))

    elements.append(Spacer(1, 0.5*cm))

    # ══════════════════════════════════════════
    # SECTION 1 — PAR PLAT
    # ══════════════════════════════════════════
    # Titre de section
    elements.append(Table(
        [[Paragraph("PAR PLAT", sSH)]],
        colWidths=[W],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), TERRE),
            ('TOPPADDING',(0,0),(-1,-1), 7), ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('LINEABOVE',(0,0),(-1,0), 2, OR), ('LINEBELOW',(0,0),(-1,0), 2, OR),
        ])
    ))
    elements.append(Spacer(1, 0.3*cm))

    ACCENTS = [TERRACOTTA, TERRE, colors.HexColor("#8B4513"), colors.HexColor("#A0522D"), colors.HexColor("#CD853F")]

    for i, (plat, group) in enumerate(shopping_df.groupby("Plat", sort=False)):
        accent = ACCENTS[i % len(ACCENTS)]
        pe = []

        # Titre du plat : pastille colorée + nom
        pe.append(Table(
            [[Paragraph(f"  {plat}", sPT)]],
            colWidths=[W],
            style=TableStyle([
                ('BACKGROUND',(0,0),(-1,-1), accent),
                ('TOPPADDING',(0,0),(-1,-1), 7), ('BOTTOMPADDING',(0,0),(-1,-1), 7),
                ('LEFTPADDING',(0,0),(-1,-1), 10),
                ('LINEBELOW',(0,0),(-1,0), 1.5, OR),
            ])
        ))

        # Ingrédients : zébrage sable/blanc
        ing_data = []
        for _, row in group.iterrows():
            qty = row['Quantité']
            qty_str = str(int(qty)) if qty == int(qty) else f"{qty:.1f}"
            ing_data.append([
                Paragraph(f"  {row['Ingrédient']}", sIL),
                Paragraph(f"{qty_str} {row['Unité']}", sQT),
            ])

        t = Table(ing_data, colWidths=[12.5*cm, 4.5*cm])
        t.setStyle(TableStyle([
            ('ROWBACKGROUNDS',(0,0),(-1,-1), [BLANC, SABLE]),
            ('TOPPADDING',(0,0),(-1,-1), 5), ('BOTTOMPADDING',(0,0),(-1,-1), 5),
            ('LEFTPADDING',(0,0),(-1,-1), 10), ('RIGHTPADDING',(0,0),(-1,-1), 8),
            ('LINEBELOW',(0,-1),(-1,-1), 0.5, OR_PALE),
            # Ligne colorée à gauche de chaque ligne impaire
            ('LINEBEFORE',(0,0),(0,-1), 2, accent),
        ]))
        pe.append(t)
        pe.append(Spacer(1, 0.25*cm))
        elements.append(KeepTogether(pe))

    # ══════════════════════════════════════════
    # SECTION 2 — LISTE GLOBALE CONSOLIDÉE
    # ══════════════════════════════════════════
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Table(
        [[Paragraph("RECAPITULATIF GLOBAL", sSH)]],
        colWidths=[W],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), ENCRE),
            ('TOPPADDING',(0,0),(-1,-1), 7), ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('LINEABOVE',(0,0),(-1,0), 2, OR), ('LINEBELOW',(0,0),(-1,0), 2, OR),
        ])
    ))
    elements.append(Spacer(1, 0.3*cm))

    # Consolidation globale (somme toutes unités identiques)
    global_df = (
        shopping_df.groupby(['Ingrédient', 'Unité'], sort=True)
        .agg(Quantité=('Quantité', 'sum'))
        .reset_index()
        .sort_values('Ingrédient')
    )

    # Affichage en 2 colonnes côte à côte
    global_rows = list(global_df.iterrows())
    mid = (len(global_rows) + 1) // 2
    left  = global_rows[:mid]
    right = global_rows[mid:]
    while len(right) < len(left):
        right.append((None, None))

    sGL = S('sGL', fontSize=9,  textColor=ENCRE,      fontName='Times-Roman', leading=13)
    sGQ = S('sGQ', fontSize=9,  textColor=TERRACOTTA, fontName='Helvetica-Bold', leading=13, alignment=TA_RIGHT)
    sGE = S('sGE', fontSize=9,  textColor=BLANC,      fontName='Times-Roman', leading=13)

    global_table_data = []
    for (_, lrow), (_, rrow) in zip(left, right):
        lqty = lrow['Quantité']
        lqty_str = str(int(lqty)) if lqty == int(lqty) else f"{lqty:.1f}"
        lcell_l = Paragraph(f"  {lrow['Ingrédient']}", sGL)
        lcell_r = Paragraph(f"{lqty_str} {lrow['Unité']}", sGQ)

        if rrow is not None:
            rqty = rrow['Quantité']
            rqty_str = str(int(rqty)) if rqty == int(rqty) else f"{rqty:.1f}"
            rcell_l = Paragraph(f"  {rrow['Ingrédient']}", sGL)
            rcell_r = Paragraph(f"{rqty_str} {rrow['Unité']}", sGQ)
        else:
            rcell_l = Paragraph("", sGE)
            rcell_r = Paragraph("", sGE)

        global_table_data.append([lcell_l, lcell_r, Paragraph("", sGE), rcell_l, rcell_r])

    gt = Table(global_table_data, colWidths=[6.2*cm, 2.3*cm, 0.8*cm, 6.2*cm, 1.5*cm])
    gt.setStyle(TableStyle([
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [PARCHEMIN, SABLE]),
        ('TOPPADDING',(0,0),(-1,-1), 5), ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING',(0,0),(-1,-1), 6), ('RIGHTPADDING',(0,0),(-1,-1), 4),
        ('LINEAFTER',(1,0),(1,-1), 0.5, OR_PALE),   # séparateur centre
        ('LINEAFTER',(2,0),(2,-1), 0.5, OR_PALE),
        ('BOX',(0,0),(-1,-1), 0.5, OR_PALE),
    ]))
    elements.append(gt)

    # ══════════════════════════════════════════
    # PIED DE PAGE
    # ══════════════════════════════════════════
    elements.append(Spacer(1, 0.6*cm))
    elements.append(Table([[""]], colWidths=[W], rowHeights=[1.5],
        style=TableStyle([('BACKGROUND',(0,0),(-1,-1), OR)])))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "La Valise aux Epices  —  Cuisine faite maison, livree avec amour",
        sRM
    ))

    doc.build(elements)
    return pdf_filename


def send_email(pdf_filename, name, firstname, address, phone, num_guests, selected_dishes):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"LVaE {name} {firstname}"

    body = f"""Nouvelle commande — Valou fait les courses !

Client : {firstname} {name}
Adresse : {address}
Téléphone : {phone}
Nombre de couverts : {num_guests}
Plats choisis : {', '.join(selected_dishes)}

La liste de courses est en pièce jointe.
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    with open(pdf_filename, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(attach)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")
        return False


# =====================================================================
# INTERFACE PRINCIPALE
# =====================================================================

# Bannière
st.markdown("""
<div class="banner">
    <h1>🥘 La Valise aux Épices</h1>
    <p>Cuisine maison · Livraison à domicile</p>
</div>
""", unsafe_allow_html=True)

menu_data = load_menu()

if menu_data is None:
    st.markdown("""
    <div class="info-box">
        🕐 Notre menu est en cours de mise à jour. Revenez très vite !
    </div>
    """, unsafe_allow_html=True)
else:
    available_dishes = list(menu_data.keys())

    with st.form("client_form"):

        # --- Section 1 : Infos client ---
        st.markdown("### 👤 Vos informations")
        col1, col2 = st.columns(2)
        with col1:
            firstname = st.text_input("Prénom", placeholder="Marie")
            name = st.text_input("Nom", placeholder="Dupont")
        with col2:
            phone = st.text_input("Téléphone", value="+33 ", placeholder="+33 6 00 00 00 00")
            address = st.text_input("Adresse complète", placeholder="12 rue des Épices, 83990 Saint-Tropez")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # --- Section 2 : Repas ---
        st.markdown("### 🍽️ Votre Repas")
        num_guests = st.selectbox(
            "Pour combien de personnes ?",
            options=list(range(1, 21)),
            index=3,
            help="Les quantités sont calculées automatiquement selon le nombre de convives."
        )

        st.markdown("""
        <div class="info-box">
            ✨ Choisissez jusqu'à <strong>5 plats</strong> parmi notre sélection ci-dessous.
        </div>
        """, unsafe_allow_html=True)

        # Affichage des plats en 3 colonnes
        cols = st.columns(3)
        selected_dishes = []
        for index, dish in enumerate(available_dishes):
            with cols[index % 3]:
                if st.checkbox(dish, key=f"dish_{index}"):
                    selected_dishes.append(dish)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # --- Section 3 : Les courses ---
        st.markdown("### 🛒 Gestion des courses")
        course_option = st.radio(
            "Comment souhaitez-vous gérer les courses ?",
            options=["Je fais les courses moi-même", "Valou fait les courses (+15€)"],
            help="Si Valou fait les courses, votre liste lui sera envoyée directement par email."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅ Valider ma commande")

    # --- VÉRIFICATIONS ---
    if submitted:
        if not selected_dishes:
            st.error("⚠️ Veuillez sélectionner au moins un plat.")
        elif len(selected_dishes) > 5:
            st.error(f"⚠️ Vous avez sélectionné {len(selected_dishes)} plats. Maximum 5 autorisés.")
        elif not name or not firstname or not address:
            st.error("⚠️ Veuillez remplir toutes vos informations (Nom, Prénom, Adresse).")
        else:
            with st.spinner("Préparation de votre liste de courses..."):
                shopping_df = calculate_groceries(menu_data, selected_dishes, num_guests)
                valou_fait_courses = course_option == "Valou fait les courses (+15€)"

                # Le PDF inclut l'adresse seulement si Valou fait les courses
                pdf_path = generate_pdf(
                    shopping_df,
                    name,
                    firstname,
                    address=address if valou_fait_courses else None,
                    num_guests=num_guests,
                    selected_dishes=selected_dishes,
                )

            if not valou_fait_courses:
                st.success("🎉 Votre liste est prête ! Téléchargez-la ci-dessous.")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Télécharger ma liste de courses (PDF)",
                        data=f,
                        file_name=f"La_Valise_aux_Epices_{firstname}.pdf",
                        mime="application/pdf"
                    )
            else:
                with st.spinner("Envoi à Valou en cours..."):
                    if send_email(pdf_path, name, firstname, address, phone, num_guests, selected_dishes):
                        st.success("✨ Parfait ! Votre demande a été transmise à Valou. Vous n'avez plus rien à faire !")
                        st.markdown("""
                        <div class="info-box">
                            🕐 Valou va faire vos courses et vous contacter très vite au numéro indiqué.
                        </div>
                        """, unsafe_allow_html=True)

            if os.path.exists(pdf_path):
                os.remove(pdf_path)
