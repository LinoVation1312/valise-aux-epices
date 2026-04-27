import streamlit as st
import pandas as pd
import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# --- CONFIGURATION ---
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVER = "lavaliseauxepices@gmail.com"
EXCEL_FILE_PATH = "menu_actuel.xlsx"
LOGO_PATH = "valise.jpg"

st.set_page_config(
    page_title="La Valise aux Épices",
    page_icon="🥘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

    .stApp { background-color: #FDFAF5; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #7A4F2E !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #E8C99A;
        padding-bottom: 6px;
        margin-top: 1.5rem !important;
    }
    p, label, div { font-family: 'Lato', sans-serif !important; color: #3B2A1A; }

    .stTextInput > div > div > input {
        border: 1.5px solid #D4A96A; border-radius: 8px;
        background-color: #FFFDF8; color: #3B2A1A;
    }
    .stTextInput > div > div > input:focus {
        border-color: #C47C2B; box-shadow: 0 0 0 2px rgba(196,124,43,0.2);
    }
    .stSelectbox > div > div { border: 1.5px solid #D4A96A; border-radius: 8px; background-color: #FFFDF8; }
    .stCheckbox > label { font-size: 0.95rem; color: #3B2A1A; }

    .stFormSubmitButton > button {
        background-color: #C47C2B !important; color: white !important;
        font-family: 'Cormorant Garamond', serif !important; font-weight: 700 !important;
        font-size: 1.15rem !important; border: none !important; border-radius: 10px !important;
        padding: 0.7rem 2.5rem !important; width: 100%; transition: background-color 0.3s; letter-spacing: 1.5px;
    }
    .stFormSubmitButton > button:hover { background-color: #A5621E !important; }

    .stDownloadButton > button {
        background-color: #C47C2B !important; color: #FFFFFF !important;
        font-family: 'Cormorant Garamond', serif !important; font-weight: 700 !important;
        font-size: 1.1rem !important; letter-spacing: 1px !important; border: none !important;
        border-radius: 10px !important; width: 100%; padding: 0.75rem 1.5rem !important;
        box-shadow: 0 3px 10px rgba(196,124,43,0.4) !important;
    }
    .stDownloadButton > button:hover { background-color: #A5621E !important; }
    .stDownloadButton > button p { color: #FFFFFF !important; }

    .stRadio > div {
        background-color: #FEF6E8; border-radius: 10px;
        padding: 12px 16px; border: 1.5px solid #E8C99A;
    }
    
/* Banner */
    .banner {
        border-radius: 18px; overflow: hidden;
        margin-bottom: 28px; box-shadow: 0 6px 28px rgba(59,42,26,0.40);
        line-height: 0;
    }
    .banner-logo {
        width: 100%; height: auto; object-fit: cover; display: block;
    }
    .divider {
        height: 2px; background: linear-gradient(90deg, transparent, #E8C99A, transparent);
        margin: 20px 0; border: none;
    }
    .info-box {
        background: #FEF6E8; border-left: 4px solid #C47C2B; border-radius: 8px;
        padding: 12px 16px; margin: 12px 0; font-size: 0.9rem;
    }

    /* Catégorie principale */
    .cat-header-entree {
        background: #9DB510; color: white; border-radius: 10px; padding: 9px 16px;
        font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: 700;
        letter-spacing: 1px; margin: 16px 0 4px 0;
    }
    .cat-header-dessert {
        background: #9E0522; color: white; border-radius: 10px; padding: 9px 16px;
        font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: 700;
        letter-spacing: 1px; margin: 16px 0 4px 0;
    }
    /* Catégorie plat principale */
    .cat-header-plat {
        background: #C47C2B; color: white; border-radius: 10px; padding: 9px 16px;
        font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: 700;
        letter-spacing: 1px; margin: 16px 0 4px 0;
    }
    /* Sous-catégories plat */
    .subcat-viande {
        background: #8B2500; color: white; border-radius: 8px; padding: 6px 14px 6px 22px;
        font-family: 'Cormorant Garamond', serif; font-size: 1rem; font-weight: 600;
        letter-spacing: 1px; margin: 8px 0 3px 0;
    }
    .subcat-poisson {
        background: #1565C0; color: white; border-radius: 8px; padding: 6px 14px 6px 22px;
        font-family: 'Cormorant Garamond', serif; font-size: 1rem; font-weight: 600;
        letter-spacing: 1px; margin: 8px 0 3px 0;
    }
    .subcat-vege {
        background: #2E7D32; color: white; border-radius: 8px; padding: 6px 14px 6px 22px;
        font-family: 'Cormorant Garamond', serif; font-size: 1rem; font-weight: 600;
        letter-spacing: 1px; margin: 8px 0 3px 0;
    }
</style>
""", unsafe_allow_html=True)


# --- CONSTANTES ---
# Ordre d'affichage des catégories
CAT_ORDER = ['Entrée', 'Plat viande', 'Plat poisson', 'Plat végé', 'Dessert']

# Mapping catégorie → groupe d'affichage (pour PDF)
CAT_TO_GROUP = {
    'Entrée':      'Entrée',
    'Plat viande': 'Plat',
    'Plat poisson':'Plat',
    'Plat végé':   'Plat',
    'Dessert':     'Dessert',
}

CAT_ICONS = {
    'Entrée':      '🥗',
    'Plat viande': '🥩',
    'Plat poisson':'🐟',
    'Plat végé':   '🥦',
    'Dessert':     '🍰',
}

CAT_LABELS = {
    'Entrée':      'Salade ou tartes',
    'Plat viande': 'Viande',
    'Plat poisson':'Poisson',
    'Plat végé':   'Végétarien',
    'Dessert':     'DESSERTS',
}


# --- FONCTIONS UTILITAIRES ---

def get_logo_base64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = LOGO_PATH.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        return f"data:{mime};base64,{data}"
    return None


def load_menu():
    """Charge le fichier Excel (nouvelle structure) en ignorant la feuille Synthèse."""
    if not os.path.exists(EXCEL_FILE_PATH):
        return None
    all_sheets = pd.read_excel(EXCEL_FILE_PATH, sheet_name=None, header=None)
    return {k: v for k, v in all_sheets.items() if k != "Synthèse"}


def get_dish_category(df):
    """
    Nouvelle structure :
      - A1 = 'Catégorie :'  /  B1 = catégorie (ex: 'Plat viande', 'Entrée', 'Dessert'...)
      - A2 = 'Ingrédient'   /  B2 = 'Quantité'  /  C2 = 'Unité'
      - A3+ = données
    Retourne la valeur de B1.
    """
    try:
        val = df.iloc[0, 1]  # ligne 0 = row 1, colonne 1 = B
        if pd.notna(val):
            return str(val).strip()
    except Exception:
        pass
    return 'Plat viande'


def get_ingredients_df(df):
    """
    Retourne un DataFrame avec colonnes ['Ingrédient', 'Quantité', 'Unité']
    à partir de la ligne 3 (index 2) du sheet.
    """
    data = df.iloc[2:].copy()
    data.columns = range(len(data.columns))
    result = pd.DataFrame({
        'Ingrédient': data[0],
        'Quantité':   data[1],
        'Unité':      data[2],
    }).dropna(subset=['Ingrédient']).reset_index(drop=True)
    return result


def normalize_ingredient(name):
    import unicodedata
    name = str(name).strip().lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    if name.endswith('s') and len(name) > 3:
        name = name[:-1]
    return name


def calculate_groceries(menu_data, selected_dishes, num_guests):
    shopping_list = []
    ratio = num_guests / 4.0
    for dish in selected_dishes:
        df = menu_data[dish]
        ing_df = get_ingredients_df(df)
        for _, row in ing_df.iterrows():
            shopping_list.append({
                "Plat": dish,
                "Ingrédient": row['Ingrédient'],
                "Quantité": row['Quantité'] * ratio,
                "Unité": row['Unité']
            })
    df_all = pd.DataFrame(shopping_list)
    df_all['_key'] = (
        df_all['Ingrédient'].apply(normalize_ingredient)
        + '__'
        + df_all['Unité'].astype(str).str.strip().str.lower()
    )
    canonical_names = df_all.groupby('_key')['Ingrédient'].agg(lambda x: x.value_counts().index[0])
    df_all['Ingrédient'] = df_all['_key'].map(canonical_names)
    df_agg = (
        df_all.groupby(['Plat', '_key'], sort=False)
        .agg(Ingrédient=('Ingrédient', 'first'), Quantité=('Quantité', 'sum'), Unité=('Unité', 'first'))
        .reset_index()
        .drop(columns='_key')
    )
    df_agg['Plat'] = pd.Categorical(df_agg['Plat'], categories=selected_dishes, ordered=True)
    df_agg = df_agg.sort_values('Plat').reset_index(drop=True)
    return df_agg


def generate_pdf(shopping_df, name, firstname, address=None, num_guests=4, selected_dishes=None, menu_data=None):
    pdf_filename = f"La_Valise_aux_Epices_{firstname}_{name}.pdf"

    ENCRE      = colors.HexColor("#1C1208")
    TERRACOTTA = colors.HexColor("#B85C38")
    TERRE      = colors.HexColor("#6B3D2E")
    OR         = colors.HexColor("#D4973A")
    OR_PALE    = colors.HexColor("#EDD79A")
    SABLE      = colors.HexColor("#F5ECD7")
    PARCHEMIN  = colors.HexColor("#FBF6EC")
    BLANC      = colors.white
    GRIS       = colors.HexColor("#888888")

    # Couleurs sous-catégories plats
    C_VIANDE  = colors.HexColor("#8B2500")
    C_POISSON = colors.HexColor("#1565C0")
    C_VEGE    = colors.HexColor("#2E7D32")
    C_ENTREE  = colors.HexColor("#9DB510")
    C_DESSERT = colors.HexColor("#9E0522")
    C_PLAT    = colors.HexColor("#C47C2B")

    CAT_PDF_COLORS = {
        'Entrée':      C_ENTREE,
        'Plat viande': C_VIANDE,
        'Plat poisson':C_POISSON,
        'Plat végé':   C_VEGE,
        'Dessert':     C_DESSERT,
    }

    W = 17 * cm
    doc = SimpleDocTemplate(
        pdf_filename, pagesize=A4,
        topMargin=1.8*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm
    )
    styles = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, parent=styles['Normal'], **kw)

    sT   = S('sT',   fontSize=26, textColor=BLANC,      fontName='Times-Bold',         alignment=TA_CENTER, leading=32)
    sST  = S('sST',  fontSize=8,  textColor=OR_PALE,    fontName='Helvetica',          alignment=TA_CENTER, leading=13, charSpace=2)
    sCL  = S('sCL',  fontSize=8,  textColor=TERRACOTTA, fontName='Helvetica-Bold',     leading=11)
    sCV  = S('sCV',  fontSize=11, textColor=ENCRE,      fontName='Times-Roman',        leading=15)
    sPT  = S('sPT',  fontSize=12, textColor=BLANC,      fontName='Times-Bold',         leading=16)
    sIL  = S('sIL',  fontSize=10, textColor=ENCRE,      fontName='Times-Roman',        leading=14)
    sQT  = S('sQT',  fontSize=10, textColor=TERRACOTTA, fontName='Helvetica-Bold',     leading=14, alignment=TA_RIGHT)
    sRM  = S('sRM',  fontSize=8,  textColor=GRIS,       fontName='Helvetica-Oblique',  alignment=TA_CENTER, leading=12)
    sSH  = S('sSH',  fontSize=11, textColor=BLANC,      fontName='Times-Bold',         leading=15, alignment=TA_CENTER)
    sCAT = S('sCAT', fontSize=10, textColor=BLANC,      fontName='Helvetica-Bold',     leading=14, alignment=TA_CENTER)
    sSUB = S('sSUB', fontSize=9,  textColor=BLANC,      fontName='Helvetica-Bold',     leading=13, alignment=TA_LEFT)

    elements = []

    # HEADER
    elements.append(Table([[""]], colWidths=[W], rowHeights=[3],
        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), OR)])))
    elements.append(Table(
        [[Paragraph("La Valise aux Epices", sT)]], colWidths=[W],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), ENCRE),
            ('TOPPADDING', (0,0), (-1,-1), 22), ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ])
    ))
    elements.append(Table(
        [[Paragraph("LISTE DE COURSES", sST)]], colWidths=[W],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), TERRACOTTA),
            ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ])
    ))
    elements.append(Table([[""]], colWidths=[W], rowHeights=[3],
        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), OR)])))
    elements.append(Spacer(1, 0.5*cm))

    # FICHE CLIENT
    col1 = 10.5*cm; col2 = 6.5*cm
    client_rows = [
        [Paragraph("CLIENT", sCL),       Paragraph("COUVERTS", sCL)],
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
        ('BACKGROUND', (0,0), (-1,-1), PARCHEMIN),
        ('BOX', (0,0), (-1,-1), 1, OR_PALE),
        ('LINEBELOW', (0,1), (-1,1), 0.5, OR_PALE),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(ct)
    elements.append(Spacer(1, 0.35*cm))

    # Bandeau plats choisis
    if selected_dishes and menu_data:
        plats_text = "  ·  ".join(
            f"{CAT_ICONS.get(get_dish_category(menu_data[d]), '🍽️')} {d}"
            for d in selected_dishes
        )
        elements.append(Table(
            [[Paragraph(plats_text, S('sP', fontSize=8, textColor=TERRE,
                fontName='Helvetica-Oblique', alignment=TA_CENTER, leading=12))]],
            colWidths=[W],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), SABLE),
                ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LINEABOVE', (0,0), (-1,0), 0.5, OR), ('LINEBELOW', (0,0), (-1,0), 0.5, OR),
                ('LEFTPADDING', (0,0), (-1,-1), 8), ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ])
        ))

    elements.append(Spacer(1, 0.5*cm))

    # SECTION PAR PLAT
    elements.append(Table(
        [[Paragraph("PAR PLAT", sSH)]], colWidths=[W],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), TERRE),
            ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LINEABOVE', (0,0), (-1,0), 2, OR), ('LINEBELOW', (0,0), (-1,0), 2, OR),
        ])
    ))
    elements.append(Spacer(1, 0.3*cm))

    # Grouper les plats sélectionnés par catégorie (ordre défini)
    dishes_by_cat = {cat: [] for cat in CAT_ORDER}
    for d in (selected_dishes or []):
        cat = get_dish_category(menu_data[d]) if menu_data else 'Plat viande'
        dishes_by_cat.setdefault(cat, []).append(d)

    ACCENTS = [TERRACOTTA, TERRE, colors.HexColor("#8B4513"), colors.HexColor("#A0522D"), colors.HexColor("#CD853F")]
    dish_counter = 0

    # Regrouper Entrée / [Plat viande + Plat poisson + Plat végé] / Dessert
    groups = [
        ('Entrée',  ['Entrée'],                        C_ENTREE,  '🥗  SALADE OU TARTES'),
        ('Plat',    ['Plat viande','Plat poisson','Plat végé'], C_PLAT, '🍽️  PLATS'),
        ('Dessert', ['Dessert'],                       C_DESSERT, '🍰  DESSERTS'),
    ]

    for group_key, cats_in_group, group_color, group_label in groups:
        all_dishes_in_group = []
        for c in cats_in_group:
            all_dishes_in_group.extend(dishes_by_cat.get(c, []))
        if not all_dishes_in_group:
            continue

        # Bandeau groupe principal
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Table(
            [[Paragraph(group_label, sCAT)]], colWidths=[W],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), group_color),
                ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LINEABOVE', (0,0), (-1,0), 1.5, OR_PALE), ('LINEBELOW', (0,0), (-1,0), 1.5, OR_PALE),
            ])
        ))
        elements.append(Spacer(1, 0.15*cm))

        for cat in cats_in_group:
            dishes = dishes_by_cat.get(cat, [])
            if not dishes:
                continue

            # Bandeau sous-catégorie (seulement si c'est un sous-groupe plat)
            if group_key == 'Plat':
                sub_color = CAT_PDF_COLORS[cat]
                sub_label = f"{CAT_ICONS[cat]}  {CAT_LABELS[cat].upper()}"
                elements.append(Table(
                    [[Paragraph(f"  {sub_label}", sSUB)]], colWidths=[W],
                    style=TableStyle([
                        ('BACKGROUND', (0,0), (-1,-1), sub_color),
                        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('LEFTPADDING', (0,0), (-1,-1), 16),
                        ('LINEBELOW', (0,0), (-1,0), 1, OR_PALE),
                    ])
                ))
                elements.append(Spacer(1, 0.1*cm))

            for plat in dishes:
                group_items = shopping_df[shopping_df['Plat'] == plat]
                accent = CAT_PDF_COLORS.get(cat, ACCENTS[dish_counter % len(ACCENTS)])
                dish_counter += 1
                pe = []

                pe.append(Table(
                    [[Paragraph(f"  {plat}", sPT)]], colWidths=[W],
                    style=TableStyle([
                        ('BACKGROUND', (0,0), (-1,-1), accent),
                        ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                        ('LEFTPADDING', (0,0), (-1,-1), 10),
                        ('LINEBELOW', (0,0), (-1,0), 1.5, OR),
                    ])
                ))

                ing_data = []
                for _, row in group_items.iterrows():
                    qty = row['Quantité']
                    qty_str = str(int(qty)) if qty == int(qty) else f"{qty:.1f}"
                    ing_data.append([
                        Paragraph(f"  {row['Ingrédient']}", sIL),
                        Paragraph(f"{qty_str} {row['Unité']}", sQT),
                    ])

                t = Table(ing_data, colWidths=[12.5*cm, 4.5*cm])
                t.setStyle(TableStyle([
                    ('ROWBACKGROUNDS', (0,0), (-1,-1), [BLANC, SABLE]),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 10), ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ('LINEBELOW', (0,-1), (-1,-1), 0.5, OR_PALE),
                    ('LINEBEFORE', (0,0), (0,-1), 2, accent),
                ]))
                pe.append(t)
                pe.append(Spacer(1, 0.25*cm))
                elements.append(KeepTogether(pe))
                elements.append(PageBreak())

    # RÉCAPITULATIF GLOBAL
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Table(
        [[Paragraph("RECAPITULATIF GLOBAL", sSH)]], colWidths=[W],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), ENCRE),
            ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LINEABOVE', (0,0), (-1,0), 2, OR), ('LINEBELOW', (0,0), (-1,0), 2, OR),
        ])
    ))
    elements.append(Spacer(1, 0.3*cm))

    global_df = (
        shopping_df.groupby(['Ingrédient', 'Unité'], sort=True)
        .agg(Quantité=('Quantité', 'sum'))
        .reset_index()
        .sort_values('Ingrédient')
    )

    global_rows = list(global_df.iterrows())
    mid = (len(global_rows) + 1) // 2
    left  = global_rows[:mid]
    right = global_rows[mid:]
    while len(right) < len(left):
        right.append((None, None))

    sGL = S('sGL', fontSize=9, textColor=ENCRE,      fontName='Times-Roman',    leading=13)
    sGQ = S('sGQ', fontSize=9, textColor=TERRACOTTA, fontName='Helvetica-Bold', leading=13, alignment=TA_RIGHT)
    sGE = S('sGE', fontSize=9, textColor=BLANC,      fontName='Times-Roman',    leading=13)

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
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [PARCHEMIN, SABLE]),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('LINEAFTER', (1,0), (1,-1), 0.5, OR_PALE),
        ('LINEAFTER', (2,0), (2,-1), 0.5, OR_PALE),
        ('BOX', (0,0), (-1,-1), 0.5, OR_PALE),
    ]))
    elements.append(gt)
    elements.append(Spacer(1, 0.25*cm))
    elements.append(Paragraph(
        "* pensez à avoir dans vos placards huile, vinaigre, sel, poivre",
        S('sNOTE', fontSize=9, textColor=GRIS, fontName='Helvetica-Oblique', alignment=TA_LEFT, leading=12)
    ))

    # PIED DE PAGE
    elements.append(Spacer(1, 0.6*cm))
    elements.append(Table([[""]], colWidths=[W], rowHeights=[1.5],
        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), OR)])))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "", sRM
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

# Banner avec logo
logo_b64 = get_logo_base64()
if logo_b64:
    st.markdown(f"""
    <div class="banner">
        <img src="{logo_b64}" class="banner-logo" alt="Logo La Valise aux Épices">
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="banner" style="background:linear-gradient(160deg,#1C1208,#C47C2B);padding:28px;text-align:center;font-family:'Cormorant Garamond',serif;color:#FEF6E8;font-size:2.5rem;font-weight:600;letter-spacing:3px;">
        🥘 La Valise aux Épices
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
    # Organiser les plats par catégorie exacte
    dishes_by_category = {cat: [] for cat in CAT_ORDER}
    for dish_name, df in menu_data.items():
        cat = get_dish_category(df)
        if cat in dishes_by_category:
            dishes_by_category[cat].append(dish_name)
        else:
            dishes_by_category.setdefault(cat, []).append(dish_name)

    with st.form("client_form"):

        # Section 1 : Infos client
        st.markdown("### 👤 Vos informations")
        col1, col2 = st.columns(2)
        with col1:
            firstname = st.text_input("Prénom", placeholder="Marie")
            name = st.text_input("Nom", placeholder="Dupont")
        with col2:
            phone = st.text_input("Téléphone", value="+33 ", placeholder="+33 6 00 00 00 00")
            address = st.text_input("Adresse complète", placeholder="12 rue des Épices, 83990 Saint-Tropez")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Section 2 : Repas
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

        selected_dishes = []

        # --- ENTRÉES ---
        if dishes_by_category.get('Entrée'):
            st.markdown('<div class="cat-header-entree">🥗 &nbsp; SALADE OU TARTES</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, dish in enumerate(dishes_by_category['Entrée']):
                with cols[i % 3]:
                    if st.checkbox(dish, key=f"dish_{dish}"):
                        selected_dishes.append(dish)

        # --- PLATS (avec sous-catégories) ---
        has_plats = any(dishes_by_category.get(c) for c in ['Plat viande', 'Plat poisson', 'Plat végé'])
        if has_plats:
            st.markdown('<div class="cat-header-plat">🍽️ &nbsp; PLATS</div>', unsafe_allow_html=True)

            if dishes_by_category.get('Plat viande'):
                st.markdown('<div class="subcat-viande">🥩 &nbsp; Viande</div>', unsafe_allow_html=True)
                cols = st.columns(3)
                for i, dish in enumerate(dishes_by_category['Plat viande']):
                    with cols[i % 3]:
                        if st.checkbox(dish, key=f"dish_{dish}"):
                            selected_dishes.append(dish)

            if dishes_by_category.get('Plat poisson'):
                st.markdown('<div class="subcat-poisson">🐟 &nbsp; Poisson</div>', unsafe_allow_html=True)
                cols = st.columns(3)
                for i, dish in enumerate(dishes_by_category['Plat poisson']):
                    with cols[i % 3]:
                        if st.checkbox(dish, key=f"dish_{dish}"):
                            selected_dishes.append(dish)

            if dishes_by_category.get('Plat végé'):
                st.markdown('<div class="subcat-vege">🥦 &nbsp; Végétarien</div>', unsafe_allow_html=True)
                cols = st.columns(3)
                for i, dish in enumerate(dishes_by_category['Plat végé']):
                    with cols[i % 3]:
                        if st.checkbox(dish, key=f"dish_{dish}"):
                            selected_dishes.append(dish)

        # --- DESSERTS ---
        if dishes_by_category.get('Dessert'):
            st.markdown('<div class="cat-header-dessert">🍰 &nbsp; DESSERTS</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, dish in enumerate(dishes_by_category['Dessert']):
                with cols[i % 3]:
                    if st.checkbox(dish, key=f"dish_{dish}"):
                        selected_dishes.append(dish)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Section 3 : Courses
        st.markdown("### 🛒 Gestion des courses")
        course_option = st.radio(
            "Comment souhaitez-vous gérer les courses ?",
            options=["Je fais les courses moi-même", "Valou fait les courses (+20€)*"],
            help="Si Valou fait les courses, votre liste lui sera envoyée directement par email."
        )
        st.markdown("""
        <p style="font-size:0.60rem; color:#888; margin-top:4px; font-style:italic;">
            * après déduction de 50 % de crédit d'impôt. Prix initial de 40€.
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅ Valider ma commande")

    # VÉRIFICATIONS & TRAITEMENT
    if submitted:
        valou_fait_courses = course_option == "Valou fait les courses (+20€)*"

        if not selected_dishes:
            st.error("⚠️ Veuillez sélectionner au moins un plat.")
        elif len(selected_dishes) > 5:
            st.error(f"⚠️ Vous avez sélectionné {len(selected_dishes)} plats. Maximum 5 autorisés.")
        elif valou_fait_courses and (not name or not firstname or not phone or not address):
            st.error("⚠️ Veuillez remplir vos informations (Nom, Prénom, Téléphone, Adresse) pour que Valou puisse vous livrer.")
        else:
            with st.spinner("Préparation de votre liste de courses..."):
                shopping_df = calculate_groceries(menu_data, selected_dishes, num_guests)
                pdf_path = generate_pdf(
                    shopping_df, name, firstname,
                    address=address if valou_fait_courses else None,
                    num_guests=num_guests,
                    selected_dishes=selected_dishes,
                    menu_data=menu_data,
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
