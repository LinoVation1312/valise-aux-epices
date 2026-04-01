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

    # Couleurs
    MARRON_FONCE = colors.HexColor("#3B2A1A")
    MARRON_MOYEN = colors.HexColor("#7A4F2E")
    OR = colors.HexColor("#C47C2B")
    OR_CLAIR = colors.HexColor("#E8C99A")
    CREME = colors.HexColor("#FEF6E8")
    BLANC = colors.white

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        topMargin=1.5*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Styles personnalisés
    style_titre = ParagraphStyle(
        'Titre',
        parent=styles['Normal'],
        fontSize=22,
        textColor=BLANC,
        alignment=TA_CENTER,
        fontName='Times-Bold',
        spaceAfter=0,
        leading=28,
    )
    style_sous_titre = ParagraphStyle(
        'SousTitre',
        parent=styles['Normal'],
        fontSize=9,
        textColor=OR_CLAIR,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=0,
        leading=14,
    )
    style_client_label = ParagraphStyle(
        'ClientLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=OR,
        fontName='Helvetica-Bold',
        spaceAfter=1,
    )
    style_client_value = ParagraphStyle(
        'ClientValue',
        parent=styles['Normal'],
        fontSize=11,
        textColor=MARRON_FONCE,
        fontName='Helvetica',
        spaceAfter=0,
    )
    style_plat_titre = ParagraphStyle(
        'PlatTitre',
        parent=styles['Normal'],
        fontSize=13,
        textColor=MARRON_FONCE,
        fontName='Helvetica-Bold',
        spaceBefore=4,
        spaceAfter=4,
    )
    style_ingredient = ParagraphStyle(
        'Ingredient',
        parent=styles['Normal'],
        fontSize=10,
        textColor=MARRON_MOYEN,
        fontName='Helvetica',
        spaceAfter=1,
        leftIndent=8,
    )
    style_note = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceBefore=8,
    )

    elements = []

    # --- HEADER BANNIÈRE ---
    header_data = [[Paragraph("La Valise aux Epices", style_titre)]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), MARRON_FONCE),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    elements.append(header_table)

    # Bande dorée sous le titre
    gold_bar_data = [[Paragraph("", style_sous_titre)]]
    gold_bar = Table([[""]], colWidths=[17*cm], rowHeights=[4])
    gold_bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), OR)]))
    elements.append(gold_bar)

    # Sous-titre sous le header
    sub_data = [[Paragraph("VOTRE LISTE DE COURSES", style_sous_titre)]]
    sub_table = Table(sub_data, colWidths=[17*cm])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), MARRON_MOYEN),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 0.5*cm))

    # --- FICHE CLIENT ---
    # Construction des données client
    client_rows = [
        [
            Paragraph("CLIENT", style_client_label),
            Paragraph("COUVERTS", style_client_label),
        ],
        [
            Paragraph(f"{firstname} {name}", style_client_value),
            Paragraph(f"{num_guests} personne{'s' if num_guests > 1 else ''}", style_client_value),
        ],
    ]
    if address:
        client_rows.append([Paragraph("ADRESSE DE LIVRAISON", style_client_label), Paragraph("", style_client_label)])
        client_rows.append([Paragraph(address, style_client_value), Paragraph("", style_client_value)])

    client_table = Table(client_rows, colWidths=[11*cm, 6*cm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CREME),
        ('BOX', (0,0), (-1,-1), 1, OR_CLAIR),
        ('LINEBELOW', (0,1), (-1,1), 0.5, OR_CLAIR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 0.4*cm))

    # --- PLATS CHOISIS (résumé) ---
    if selected_dishes:
        plats_text = "  •  ".join(selected_dishes)
        plats_style = ParagraphStyle(
            'Plats', parent=styles['Normal'],
            fontSize=9, textColor=MARRON_MOYEN, fontName='Helvetica-Oblique',
            alignment=TA_CENTER
        )
        plats_data = [[Paragraph(f"Menu choisi : {plats_text}", plats_style)]]
        plats_table = Table(plats_data, colWidths=[17*cm])
        plats_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F5ECD7")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LINEABOVE', (0,0), (-1,0), 1, OR),
            ('LINEBELOW', (0,0), (-1,0), 1, OR),
        ]))
        elements.append(plats_table)

    elements.append(Spacer(1, 0.5*cm))

    # --- LISTE DE COURSES PAR PLAT ---
    for i, (plat, group) in enumerate(shopping_df.groupby("Plat", sort=False)):

        plat_elements = []

        # Titre du plat
        titre_data = [[Paragraph(f"  {plat}", style_plat_titre)]]
        titre_table = Table(titre_data, colWidths=[17*cm])
        bg_color = MARRON_FONCE if i % 2 == 0 else MARRON_MOYEN
        titre_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        # Override text color for title in the table
        titre_data_white = [[Paragraph(
            f"  {plat}",
            ParagraphStyle('PT', parent=styles['Normal'],
                fontSize=12, textColor=BLANC, fontName='Times-Bold',
                spaceBefore=0, spaceAfter=0, leading=16)
        )]]
        titre_table2 = Table(titre_data_white, colWidths=[17*cm])
        titre_table2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
        ]))
        plat_elements.append(titre_table2)

        # Ingrédients en tableau 2 colonnes
        rows = list(group.iterrows())
        ing_data = []
        style_ing_cell = ParagraphStyle(
            'IngCell', parent=styles['Normal'],
            fontSize=10, textColor=MARRON_FONCE, fontName='Helvetica',
        )
        style_qty_cell = ParagraphStyle(
            'QtyCell', parent=styles['Normal'],
            fontSize=10, textColor=OR, fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
        )

        for _, row in group.iterrows():
            qty = row['Quantité']
            qty_str = str(int(qty)) if qty == int(qty) else f"{qty:.1f}"
            ing_data.append([
                Paragraph(f"• {row['Ingrédient']}", style_ing_cell),
                Paragraph(f"{qty_str} {row['Unité']}", style_qty_cell),
            ])

        # Tableau simple 1 colonne (ingredient + quantité)
        # colWidths: 12cm nom + 5cm quantité = 17cm total (correspond à la largeur utile avec marges 2cm*2)
        ing_table = Table(ing_data, colWidths=[12*cm, 5*cm])

        ing_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BLANC),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [BLANC, CREME]),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,-1), (-1,-1), 0.5, OR_CLAIR),
        ]))
        plat_elements.append(ing_table)
        plat_elements.append(Spacer(1, 0.3*cm))

        elements.append(KeepTogether(plat_elements))

    # --- PIED DE PAGE ---
    elements.append(Spacer(1, 0.8*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=OR, spaceAfter=8))
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor("#999999"),
        fontName='Helvetica-Oblique', alignment=TA_CENTER
    )
    elements.append(Paragraph(
        "La Valise aux Epices — Cuisine faite maison, livree avec amour",
        footer_style
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
            st.error(f"⚠️ Vous avez sélectionné {len(selected_dishes)} plats. Maximum 5 pour la semaine.")
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
