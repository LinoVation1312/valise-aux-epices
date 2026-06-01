import streamlit as st
import pandas as pd
import os
import base64
import smtplib
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# --- CONFIGURATION ---
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVER = "lavaliseauxepices@gmail.com"
EXCEL_FILE_PATH = "menu_actuel.xlsx"
LOGO_PATH = "valise.png"

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

    p, label { font-family: 'Lato', sans-serif !important; color: #3B2A1A !important; }

    .stTextInput > div > div > input {
        border: 1.5px solid #D4A96A; border-radius: 8px;
        background-color: #FFFDF8 !important; color: #3B2A1A !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #C47C2B; box-shadow: 0 0 0 2px rgba(196,124,43,0.2);
    }
    .stTextInput > div > div > input::placeholder {
        color: #B09070 !important;
    }

    .stTextArea > div > div > textarea {
        border: 1.5px solid #D4A96A; border-radius: 8px;
        background-color: #FFFDF8 !important; color: #3B2A1A !important;
        font-family: 'Lato', sans-serif !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #C47C2B; box-shadow: 0 0 0 2px rgba(196,124,43,0.2);
    }
    .stTextArea > div > div > textarea::placeholder {
        color: #B09070 !important;
    }

    .stSelectbox > div > div {
        border: 1.5px solid #D4A96A !important;
        border-radius: 8px !important;
        background-color: #FFFDF8 !important;
    }
    .stSelectbox > div > div > div {
        color: #3B2A1A !important;
        background-color: #FFFDF8 !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #FFFDF8 !important;
    }
    [data-baseweb="option"] {
        background-color: #FFFDF8 !important;
        color: #3B2A1A !important;
    }
    [data-baseweb="option"]:hover {
        background-color: #FEF0D5 !important;
        color: #3B2A1A !important;
    }
    [data-baseweb="select"] span {
        color: #3B2A1A !important;
    }

    .stCheckbox > label {
        font-size: 0.95rem !important;
        color: #3B2A1A !important;
        font-family: 'Lato', sans-serif !important;
    }
    .stCheckbox > label > div { color: #3B2A1A !important; }
    .stCheckbox span { color: #3B2A1A !important; }

    .stRadio > div {
        background-color: #FEF6E8;
        border-radius: 10px;
        padding: 12px 16px;
        border: 1.5px solid #E8C99A;
    }
    .stRadio label { color: #3B2A1A !important; }
    .stRadio span { color: #3B2A1A !important; }

    .stTooltipIcon { color: #C47C2B !important; }

    .stFormSubmitButton > button {
        background-color: #C47C2B !important; color: white !important;
        font-family: 'Cormorant Garamond', serif !important; font-weight: 700 !important;
        font-size: 1.15rem !important; border: none !important; border-radius: 10px !important;
        padding: 0.7rem 2.5rem !important; width: 100%; transition: background-color 0.3s; letter-spacing: 1.5px;
    }
    .stFormSubmitButton > button:hover { background-color: #A5621E !important; }
    .stFormSubmitButton > button p { color: white !important; }

    .stDownloadButton > button {
        background-color: #C47C2B !important; color: #FFFFFF !important;
        font-family: 'Cormorant Garamond', serif !important; font-weight: 700 !important;
        font-size: 1.1rem !important; letter-spacing: 1px !important; border: none !important;
        border-radius: 10px !important; width: 100%; padding: 0.75rem 1.5rem !important;
        box-shadow: 0 3px 10px rgba(196,124,43,0.4) !important;
    }
    .stDownloadButton > button:hover { background-color: #A5621E !important; }
    .stDownloadButton > button p { color: #FFFFFF !important; }

    .stAlert > div { color: #3B2A1A !important; }
    .stSuccess > div { color: #1a4a1a !important; }
    .stError > div { color: #6a0000 !important; }
    .stWarning > div { color: #5a3a00 !important; }

    .stSpinner > div { color: #C47C2B !important; }

    .banner {
        border-radius: 18px; overflow: hidden;
        margin-bottom: 28px; box-shadow: 0 6px 28px rgba(59,42,26,0.40);
        line-height: 0;
    }
    .banner-logo { width: 100%; height: auto; object-fit: cover; display: block; }

    .divider {
        height: 2px; background: linear-gradient(90deg, transparent, #E8C99A, transparent);
        margin: 20px 0; border: none;
    }
    .info-box {
        background: #FEF6E8; border-left: 4px solid #C47C2B; border-radius: 8px;
        padding: 12px 16px; margin: 12px 0; font-size: 0.9rem;
        color: #3B2A1A !important;
    }

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
    .cat-header-plat {
        background: #C47C2B; color: white; border-radius: 10px; padding: 9px 16px;
        font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: 700;
        letter-spacing: 1px; margin: 16px 0 4px 0;
    }
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
CAT_ORDER = ['Entrée', 'Plat viande', 'Plat poisson', 'Plat végé', 'Dessert']

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

MAX_DISHES = 7  # Nombre maximum de plats sélectionnables

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
    if not os.path.exists(EXCEL_FILE_PATH):
        return None
    all_sheets = pd.read_excel(EXCEL_FILE_PATH, sheet_name=None, header=None)
    return {k: v for k, v in all_sheets.items() if k != "Synthèse"}

def get_dish_category(df):
    try:
        val = df.iloc[0, 1]
        if pd.notna(val):
            return str(val).strip()
    except Exception:
        pass
    return 'Plat viande'

def get_ingredients_df(df):
    data = df.iloc[2:].copy()
    data.columns = range(len(data.columns))
    result = pd.DataFrame({
        'Ingrédient': data[0],
        'Quantité':   pd.to_numeric(data[1], errors='coerce').fillna(0),
        'Unité':      data[2].fillna('').astype(str),
    }).dropna(subset=['Ingrédient']).reset_index(drop=True)
    return result

def normalize_ingredient(name):
    import unicodedata
    name = str(name).strip().lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    if name.endswith('s') and len(name) > 3:
        name = name[:-1]
    return name

# Unités dénombrables → on arrondit au plafond (impossible d'acheter 0.2 oignon)
COUNTABLE_UNITS = {
    'pièce(s)', 'piece(s)', 'pièce', 'piece',
    'botte', 'bottes',
    'sachet', 'sachets',
    'boîte', 'boite', 'boîtes', 'boites',
    'tranche(s)', 'tranche', 'tranches',
    'feuille', 'feuilles',
    'branche', 'branches',
    'tête', 'tetes', 'têtes',
    'gousse', 'gousses', 'gousse(s)',
    'tranche(s)', 'botte(s)', 'sachet(s)', 'boîte(s)', 'boite(s)',
    'feuille(s)', 'branche(s)', 'tête(s)', 'tete(s)',
}

def round_quantity(qty, unit):
    """Arrondit au plafond les unités dénombrables, garde 1 décimale pour le reste."""
    u = str(unit).strip().lower()
    if u in COUNTABLE_UNITS:
        return math.ceil(qty) if qty > 0 else 0
    return qty

def calculate_groceries(menu_data, selected_dishes, num_guests):
    shopping_list = []
    base_persons = 4.0

    for dish in selected_dishes:
        df = menu_data[dish]
        cat = get_dish_category(df)

        if cat == 'Dessert':
            nb_recipes = math.ceil(num_guests / base_persons)
            ratio = float(nb_recipes)
        else:
            ratio = num_guests / base_persons

        ing_df = get_ingredients_df(df)
        for _, row in ing_df.iterrows():
            shopping_list.append({
                "Plat":       dish,
                "Ingrédient": row['Ingrédient'],
                "Quantité":   row['Quantité'] * ratio,
                "Unité":      row['Unité'],
                "_cat":       cat,
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
    df_agg['Quantité'] = df_agg.apply(
        lambda r: round_quantity(r['Quantité'], r['Unité']), axis=1
    )
    df_agg['Plat'] = pd.Categorical(df_agg['Plat'], categories=selected_dishes, ordered=True)
    df_agg = df_agg.sort_values('Plat').reset_index(drop=True)
    return df_agg

def dessert_note_for_pdf(selected_dishes, menu_data, num_guests):
    dessert_dishes = [d for d in selected_dishes if get_dish_category(menu_data[d]) == 'Dessert']
    if not dessert_dishes:
        return None
    nb_recipes = math.ceil(num_guests / 4)
    if nb_recipes == 1:
        return f"🍰 Desserts : quantités pour 1 recette (base 4 pers.) — suffit pour {num_guests} convive{'s' if num_guests > 1 else ''}."
    else:
        return f"🍰 Desserts : quantités pour {nb_recipes} recettes (base 4 pers. × {nb_recipes}) — pour {num_guests} convives."

def generate_pdf(shopping_df, name, firstname, address=None, email=None, phone=None,
                 num_guests=4, selected_dishes=None, menu_data=None, course_mode="self",
                 allergies=None, preferences=None):
    pdf_filename = f"La_Valise_aux_Epices_{firstname}_{name}.pdf"

    ENCRE      = colors.HexColor("#1C1208")
    TERRACOTTA = colors.HexColor("#B85C38")
    OR         = colors.HexColor("#D4973A")
    OR_PALE    = colors.HexColor("#EDD79A")
    SABLE      = colors.HexColor("#F5ECD7")
    PARCHEMIN  = colors.HexColor("#FBF6EC")
    BLANC      = colors.white
    GRIS       = colors.HexColor("#888888")
    VERT       = colors.HexColor("#2E7D32")
    ROUGE_ALERT = colors.HexColor("#9E0522")

    if course_mode == "self":
        BANDEAU_BG   = VERT
        BANDEAU_TEXT = "✔  FAIT SES COURSES"
    elif course_mode == "drive":
        BANDEAU_BG   = colors.HexColor("#1565C0")
        BANDEAU_TEXT = "🛒  VALOU PASSE AU DRIVE"
    else:
        BANDEAU_BG   = TERRACOTTA
        BANDEAU_TEXT = "🛍  VALOU FAIT LES COURSES"

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
    sRM  = S('sRM',  fontSize=8,  textColor=GRIS,       fontName='Helvetica-Oblique',  alignment=TA_CENTER, leading=12)
    sSH  = S('sSH',  fontSize=11, textColor=BLANC,      fontName='Times-Bold',         leading=15, alignment=TA_CENTER)
    sBAND = S('sBAND', fontSize=11, textColor=BLANC,    fontName='Helvetica-Bold',     leading=15, alignment=TA_CENTER)
    sALERT_LABEL = S('sALERT_LABEL', fontSize=8, textColor=BLANC, fontName='Helvetica-Bold', leading=11)
    sALERT_VAL   = S('sALERT_VAL',  fontSize=10, textColor=ENCRE, fontName='Times-Roman',    leading=14)

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
    elements.append(Table(
        [[Paragraph(BANDEAU_TEXT, sBAND)]], colWidths=[W],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BANDEAU_BG),
            ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ])
    ))
    elements.append(Table([[""]], colWidths=[W], rowHeights=[3],
        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), OR)])))
    elements.append(Spacer(1, 0.5*cm))

    # FICHE CLIENT
    col1 = 8.5*cm; col2 = 4*cm; col3 = 4.5*cm
    client_rows = [
        [Paragraph("CLIENT", sCL), Paragraph("COUVERTS", sCL), Paragraph("TÉLÉPHONE", sCL)],
        [Paragraph(f"{firstname} {name}", sCV), Paragraph(f"{num_guests} personne{'s' if num_guests > 1 else ''}", sCV), Paragraph(phone or "", sCV)],
        [Paragraph("EMAIL", sCL), Paragraph("ADRESSE", sCL), Paragraph("", sCL)],
        [Paragraph(email or "", sCV), Paragraph(address or "", sCV), Paragraph("", sCV)],
    ]
    ct = Table(client_rows, colWidths=[col1, col2, col3])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PARCHEMIN),
        ('BOX', (0,0), (-1,-1), 1, OR_PALE),
        ('LINEBELOW', (0,1), (-1,1), 0.5, OR_PALE),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (1,2), (2,2)), ('SPAN', (1,3), (2,3)),
    ]))
    elements.append(ct)
    elements.append(Spacer(1, 0.35*cm))

    # ALLERGIES & PRÉFÉRENCES (si renseignées)
    has_allergies = allergies and allergies.strip()
    has_preferences = preferences and preferences.strip()
    if has_allergies or has_preferences:
        elements.append(Table(
            [[Paragraph("⚠  ALLERGIES & PRÉFÉRENCES", sSH)]], colWidths=[W],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), ROUGE_ALERT),
                ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LINEABOVE', (0,0), (-1,0), 2, OR), ('LINEBELOW', (0,0), (-1,0), 2, OR),
            ])
        ))
        alert_rows = []
        if has_allergies:
            alert_rows.append([Paragraph("ALLERGIES", sALERT_LABEL), Paragraph(allergies.strip(), sALERT_VAL)])
        if has_preferences:
            alert_rows.append([Paragraph("PRÉFÉRENCES / MODIFICATIONS", sALERT_LABEL), Paragraph(preferences.strip(), sALERT_VAL)])
        at = Table(alert_rows, colWidths=[5*cm, 12*cm])
        at.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#C0392B")),
            ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#FDEDEC")),
            ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 10), ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, OR_PALE),
            ('LINEBELOW', (0,0), (-1,-2), 0.5, OR_PALE),
        ]))
        elements.append(at)
        elements.append(Spacer(1, 0.35*cm))

    # PLATS CHOISIS
    if selected_dishes:
        elements.append(Table(
            [[Paragraph("PLATS COMMANDÉS", sSH)]], colWidths=[W],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), ENCRE),
                ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LINEABOVE', (0,0), (-1,0), 2, OR), ('LINEBELOW', (0,0), (-1,0), 2, OR),
            ])
        ))
        elements.append(Spacer(1, 0.2*cm))
        sDISH = S('sDISH', fontSize=10, textColor=ENCRE, fontName='Times-Roman', leading=14)
        for i, dish in enumerate(selected_dishes):
            bg = PARCHEMIN if i % 2 == 0 else SABLE
            elements.append(Table(
                [[Paragraph(f"  • {dish}", sDISH)]], colWidths=[W],
                style=TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), bg),
                    ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 10),
                ])
            ))
        elements.append(Spacer(1, 0.4*cm))

    # RÉCAPITULATIF GLOBAL
    elements.append(Spacer(1, 0.2*cm))
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
    left   = global_rows[:mid]
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

    gt = Table(global_table_data, colWidths=[6.2*cm, 2.3*cm, 0.8*cm, 5.2*cm, 2.5*cm])
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

    # Note placards standard
    elements.append(Paragraph(
        "* pensez à avoir dans vos placards huile, vinaigre, sel, poivre",
        S('sNOTE', fontSize=9, textColor=GRIS, fontName='Helvetica-Oblique', alignment=TA_LEFT, leading=12)
    ))

    # Note desserts si applicable
    if menu_data and selected_dishes:
        dessert_note = dessert_note_for_pdf(selected_dishes, menu_data, num_guests)
        if dessert_note:
            elements.append(Paragraph(
                dessert_note,
                S('sNOTE2', fontSize=9, textColor=GRIS, fontName='Helvetica-Oblique', alignment=TA_LEFT, leading=12)
            ))

    elements.append(Spacer(1, 0.6*cm))
    elements.append(Table([[""]], colWidths=[W], rowHeights=[1.5],
        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), OR)])))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("", sRM))

    doc.build(elements)
    return pdf_filename

def send_email_to_valise_and_client(pdf_filename, name, firstname, address, email, phone,
                                    num_guests, selected_dishes, course_mode,
                                    allergies=None, preferences=None):
    """Envoie l'email à l'entreprise ET au client selon son choix de courses."""
    if course_mode == "self":
        mode_label = "Fait ses courses lui-même"
    elif course_mode == "drive":
        mode_label = "Valou passe au drive (+15€)"
    else:
        mode_label = "Valou fait les courses (+25€)"

    allergies_line = f"\nAllergies     : {allergies}" if allergies and allergies.strip() else ""
    preferences_line = f"\nPréférences   : {preferences}" if preferences and preferences.strip() else ""

    # --- 1. EMAIL POUR L'ENTREPRISE ---
    msg_admin = MIMEMultipart()
    msg_admin['From'] = EMAIL_SENDER
    msg_admin['To'] = EMAIL_RECEIVER
    msg_admin['Subject'] = f"LVaE {name} {firstname} — {mode_label}"

    body_admin = f"""Nouvelle commande — La Valise aux Épices

━━━━━━━━━━━━━━━━━━━━━━━━━
INFORMATIONS CLIENT
━━━━━━━━━━━━━━━━━━━━━━━━━
Nom       : {firstname} {name}
Email     : {email}
Téléphone : {phone}
Adresse   : {address}
Couverts  : {num_guests} personne{'s' if num_guests > 1 else ''}{allergies_line}{preferences_line}

━━━━━━━━━━━━━━━━━━━━━━━━━
GESTION DES COURSES
━━━━━━━━━━━━━━━━━━━━━━━━━
{mode_label}

━━━━━━━━━━━━━━━━━━━━━━━━━
PLATS CHOISIS
━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f'  • {d}' for d in selected_dishes)}

La liste de courses complète est en pièce jointe.
"""
    msg_admin.attach(MIMEText(body_admin, 'plain', 'utf-8'))
    with open(pdf_filename, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg_admin.attach(attach)

    # --- 2. EMAIL POUR LE CLIENT ---
    msg_client = MIMEMultipart()
    msg_client['From'] = EMAIL_SENDER
    msg_client['To'] = email
    msg_client['Subject'] = f"Votre commande La Valise aux Épices"

    if course_mode == "self":
        body_client = f"""Bonjour {firstname},

Merci pour votre commande ! Comme convenu, vous avez choisi de faire vos courses vous-même.

Vous trouverez votre liste de courses complète au format PDF en pièce jointe de cet e-mail.

━━━━━━━━━━━━━━━━━━━━━━━━━
RÉCAPITULATIF DE VOS PLATS
━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f'  • {d}' for d in selected_dishes)}

Nombre de couverts : {num_guests} personne{'s' if num_guests > 1 else ''}

Bonne cuisine et à très vite !
La Valise aux Épices
"""
        msg_client.attach(MIMEText(body_client, 'plain', 'utf-8'))
        with open(pdf_filename, "rb") as f:
            attach_client = MIMEApplication(f.read(), _subtype="pdf")
            attach_client.add_header('Content-Disposition', 'attachment', filename=f"Ma_liste_de_courses_{firstname}.pdf")
            msg_client.attach(attach_client)
    else:
        body_client = f"""Bonjour {firstname},

Merci pour votre commande ! 

✨ Bonne nouvelle : vous avez choisi l'option "{mode_label}". Vous n'avez donc rien à faire, Valou s'occupe de vos courses !

━━━━━━━━━━━━━━━━━━━━━━━━━
VOTRE REPAS COMMANDÉ
━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f'  • {d}' for d in selected_dishes)}

Nombre de couverts : {num_guests} personne{'s' if num_guests > 1 else ''}

Valou prendra contact avec vous très prochainement au {phone} pour finaliser l'organisation.

À très bientôt !
La Valise aux Épices
"""
        msg_client.attach(MIMEText(body_client, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg_admin)
        server.send_message(msg_client)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi des e-mails : {e}")
        return False


# =====================================================================
# INTERFACE PRINCIPALE
# =====================================================================

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
    dishes_by_category = {cat: [] for cat in CAT_ORDER}
    for dish_name, df in menu_data.items():
        cat = get_dish_category(df)
        if cat in dishes_by_category:
            dishes_by_category[cat].append(dish_name)
        else:
            dishes_by_category.setdefault(cat, []).append(dish_name)

    with st.form("client_form"):

        st.markdown("### 👤 Vos informations")
        st.markdown("""
        <div class="info-box">
            📋 Tous les champs sont obligatoires — ils nous permettent de vous envoyer votre récapitulatif et de préparer votre commande.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            firstname = st.text_input("Prénom *", placeholder="Marie")
            name      = st.text_input("Nom *", placeholder="Dupont")
            email     = st.text_input("Email *", placeholder="marie.dupont@email.com")
        with col2:
            phone   = st.text_input("Téléphone *", value="+33 ", placeholder="+33 6 00 00 00 00")
            address = st.text_input("Adresse complète *", placeholder="12 rue des Épices, 83990 Saint-Tropez")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        st.markdown("### 🍽️ Votre Repas")
        num_guests = st.selectbox(
            "Pour combien de personnes ?",
            options=list(range(1, 21)),
            index=3,
            help="Les quantités sont calculées automatiquement selon le nombre de convives."
        )

        st.markdown(f"""
        <div class="info-box">
            ✨ Choisissez jusqu'à <strong>{MAX_DISHES} plats</strong> parmi notre sélection ci-dessous.<br>
            <small>👉 <em>L'entrée et le dessert comptent chacun comme 1 plat dans ce total.</em></small>
        </div>
        """, unsafe_allow_html=True)

        selected_dishes = []

        if dishes_by_category.get('Entrée'):
            st.markdown('<div class="cat-header-entree">🥗 &nbsp; SALADE OU TARTES</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, dish in enumerate(dishes_by_category['Entrée']):
                with cols[i % 3]:
                    if st.checkbox(dish, key=f"dish_{dish}"):
                        selected_dishes.append(dish)

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

        if dishes_by_category.get('Dessert'):
            st.markdown('<div class="cat-header-dessert">🍰 &nbsp; DESSERTS</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, dish in enumerate(dishes_by_category['Dessert']):
                with cols[i % 3]:
                    if st.checkbox(dish, key=f"dish_{dish}"):
                        selected_dishes.append(dish)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        st.markdown("### 🛒 Gestion des courses")
        course_option = st.radio(
            "Comment souhaitez-vous gérer les courses ?",
            options=["Je fais les courses moi-même", "Valou fait les courses (+25€)*", "Valou passe au drive (+15€)*"],
            help="Si Valou fait les courses, votre liste lui sera envoyée directement par email."
        )
        st.markdown("""
        <p style="font-size:0.60rem; color:#888; margin-top:4px; font-style:italic;">
            * avant déduction de 50 % de crédit d'impôt. 
        </p>
        """, unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        st.markdown("### 🌿 Allergies & Préférences")
        st.markdown("""
        <div class="info-box">
            Ces champs sont <strong>facultatifs</strong>. Renseignez-les si vous avez des allergies ou des préférences alimentaires (ex : sans coriandre, sans noix, je n'aime pas le fenouil…).
        </div>
        """, unsafe_allow_html=True)

        allergies = st.text_area(
            "Allergies alimentaires",
            placeholder="Ex : allergie aux noix, intolérance au gluten, allergie aux crustacés…",
            height=80,
            key="allergies"
        )
        preferences = st.text_area(
            "Préférences / modifications",
            placeholder="Ex : sans coriandre, je n'aime pas le fenouil, éviter les plats trop épicés…",
            height=80,
            key="preferences"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅ Valider ma commande")

    # VÉRIFICATIONS & TRAITEMENT
    if submitted:
        if course_option == "Valou fait les courses (+25€)*":
            course_mode = "valou"
        elif course_option == "Valou passe au drive (+15€)**":
            course_mode = "drive"
        else:
            course_mode = "self"

        errors = []
        if not selected_dishes:
            errors.append("Veuillez sélectionner au moins un plat.")
        if len(selected_dishes) > MAX_DISHES:
            errors.append(f"Vous avez sélectionné {len(selected_dishes)} plats. Maximum {MAX_DISHES} autorisés (entrée et dessert comptent chacun comme 1 plat).")
        if not firstname or not firstname.strip():
            errors.append("Le prénom est obligatoire.")
        if not name or not name.strip():
            errors.append("Le nom est obligatoire.")
        if not email or "@" not in email:
            errors.append("Une adresse email valide est obligatoire.")
        if not phone or len(phone.strip()) < 8:
            errors.append("Un numéro de téléphone valide est obligatoire.")
        if not address or not address.strip():
            errors.append("L'adresse est obligatoire.")

        if errors:
            for err in errors:
                st.error(f"⚠️ {err}")
        else:
            with st.spinner("Préparation de votre commande..."):
                shopping_df = calculate_groceries(menu_data, selected_dishes, num_guests)
                pdf_path = generate_pdf(
                    shopping_df, name, firstname,
                    address=address, email=email, phone=phone,
                    num_guests=num_guests, selected_dishes=selected_dishes,
                    menu_data=menu_data, course_mode=course_mode,
                    allergies=allergies, preferences=preferences,
                )

            with st.spinner("Envoi des e-mails de confirmation..."):
                send_email_to_valise_and_client(
                    pdf_path, name, firstname, address, email, phone,
                    num_guests, selected_dishes, course_mode,
                    allergies=allergies, preferences=preferences,
                )

            if course_mode == "self":
                st.success("🎉 Votre commande est validée !")
                st.markdown(f"""
                <div class="info-box">
                    📧 Un e-mail contenant votre <strong>liste de courses complète (PDF)</strong> vient de vous être envoyé à l'adresse <strong>{email}</strong>.
                </div>
                """, unsafe_allow_html=True)

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="📥 Télécharger ma liste de courses immédiatement (PDF)",
                    data=pdf_bytes,
                    file_name=f"La_Valise_aux_Epices_{firstname}.pdf",
                    mime="application/pdf"
                )
            else:
                st.success("✨ Parfait ! Votre demande a bien été transmise.")
                st.markdown(f"""
                <div class="info-box">
                    📧 Un récapitulatif écrit de vos plats commandés a été envoyé à <strong>{email}</strong>.<br>
                    🕐 <strong>Valou va faire vos courses</strong> et vous contactera très vite au <strong>{phone}</strong>. Vous n'avez plus rien à faire !
                </div>
                """, unsafe_allow_html=True)

            if os.path.exists(pdf_path):
                os.remove(pdf_path)


# =====================================================================
# ADMIN
# =====================================================================

SUPPORTED_EXTENSIONS = ["xlsx", "xls", "ods", "csv"]

def read_any_file(file_or_bytes, filename=""):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "xlsx"
    if ext == "csv":
        df = pd.read_csv(file_or_bytes, header=None)
        return {"Feuille1": df}
    engine = {"ods": "odf", "xls": "xlrd"}.get(ext)
    kwargs = {"engine": engine} if engine else {}
    return pd.read_excel(file_or_bytes, sheet_name=None, header=None, **kwargs)

def convert_to_xlsx_bytes(sheets_dict):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    return buf.getvalue()

def validate_menu_excel(file_or_bytes, filename=""):
    try:
        all_sheets = read_any_file(file_or_bytes, filename)
        sheets = {k: v for k, v in all_sheets.items() if k != "Synthèse"}

        if len(sheets) == 0:
            return False, "Le fichier ne contient aucun onglet de plat."

        valid_cats = set(CAT_ORDER)
        errors = []

        for dish_name, df in sheets.items():
            try:
                cat = str(df.iloc[0, 1]).strip()
                if cat not in valid_cats:
                    errors.append(f"« {dish_name} » — catégorie invalide : « {cat} »")
            except Exception:
                errors.append(f"« {dish_name} » — impossible de lire la catégorie (cellule B1)")
                continue

            ing_df = df.iloc[2:].dropna(subset=[0])
            if len(ing_df) == 0:
                errors.append(f"« {dish_name} » — aucun ingrédient trouvé")

        if errors:
            return False, "\n".join(f"• {e}" for e in errors)

        return True, len(sheets)

    except Exception as e:
        return False, f"Impossible de lire le fichier : {e}"

st.markdown("---")

with st.expander("🔒 Administration"):

    password = st.text_input("Mot de passe admin", type="password", key="admin_password")

    if password == st.secrets.get("ADMIN_PASSWORD", "valise2026"):

        st.success("✅ Connecté")
        st.markdown("#### Remplacer le menu")
        st.markdown(f"""
        <div class="info-box">
            📋 Formats acceptés : <strong>.xlsx, .xls, .ods, .csv</strong>.<br>
            Le fichier sera automatiquement converti et publié sous le nom
            <strong>menu_actuel.xlsx</strong> sur GitHub.<br>
            Catégories valides : <strong>{', '.join(CAT_ORDER)}</strong>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choisir le nouveau fichier menu",
            type=SUPPORTED_EXTENSIONS,
            key="admin_uploader"
        )

        if uploaded_file is not None:
            original_filename = uploaded_file.name
            file_bytes = uploaded_file.read()
            uploaded_file.seek(0)

            try:
                preview_sheets = read_any_file(io.BytesIO(file_bytes), original_filename)
                preview_sheets = {k: v for k, v in preview_sheets.items() if k != "Synthèse"}
            except Exception as e:
                st.error(f"Impossible de lire le fichier : {e}")
                st.stop()

            st.markdown("#### 👀 Aperçu du fichier")
            st.caption(f"Fichier chargé : **{original_filename}** →  sera publié comme `menu_actuel.xlsx`")
            plat_names = list(preview_sheets.keys())
            st.markdown(f"**{len(plat_names)} plat(s) détecté(s) :** {', '.join(plat_names)}")

            plat_choisi = st.selectbox(
                "Voir les ingrédients d'un plat :",
                options=plat_names,
                key="admin_preview_select"
            )
            if plat_choisi:
                df_prev = preview_sheets[plat_choisi]
                cat_prev = str(df_prev.iloc[0, 1]).strip() if pd.notna(df_prev.iloc[0, 1]) else "?"
                st.markdown(f"Catégorie : **{cat_prev}**")
                ing_prev = pd.DataFrame({
                    'Ingrédient': df_prev.iloc[2:, 0],
                    'Quantité':   df_prev.iloc[2:, 1],
                    'Unité':      df_prev.iloc[2:, 2],
                }).dropna(subset=['Ingrédient']).reset_index(drop=True)
                st.dataframe(ing_prev, use_container_width=True)

            st.markdown("#### 🔍 Vérification automatique")
            ok, result = validate_menu_excel(io.BytesIO(file_bytes), original_filename)

            if ok:
                st.success(f"✅ Fichier valide — {result} plat(s) prêt(s) à être publiés.")
            else:
                st.error(f"❌ Erreurs détectées :\n\n{result}")
                st.warning("Corrigez le fichier avant de publier.")

            if ok:
                if st.button("📤 Publier le nouveau menu", key="admin_publish"):
                    try:
                        from github import Github

                        ext = original_filename.rsplit(".", 1)[-1].lower()
                        if ext == "xlsx":
                            xlsx_content = file_bytes
                        else:
                            with st.spinner("Conversion en xlsx…"):
                                xlsx_content = convert_to_xlsx_bytes(preview_sheets)

                        g = Github(st.secrets["GITHUB_TOKEN"])
                        repo = g.get_repo(st.secrets["GITHUB_REPO"])
                        github_path = "menu_actuel.xlsx"

                        try:
                            contents = repo.get_contents(github_path)
                            repo.update_file(
                                path=github_path,
                                message=f"Mise à jour menu via admin ({original_filename})",
                                content=xlsx_content,
                                sha=contents.sha
                            )
                        except Exception:
                            repo.create_file(
                                path=github_path,
                                message=f"Création menu via admin ({original_filename})",
                                content=xlsx_content
                            )

                        st.success(f"✅ **{original_filename}** publié avec succès sous `menu_actuel.xlsx` !")
                        st.info("Le site se rechargera automatiquement dans quelques secondes.")

                    except Exception as e:
                        st.error(f"Erreur lors de la publication : {e}")

    elif password != "":
        st.error("❌ Mot de passe incorrect.")
