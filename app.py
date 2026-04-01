import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF

# --- CONFIGURATION ---
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
EMAIL_RECEIVER = "lino.conord@gmail.com"
EXCEL_FILE_PATH = "menu_actuel.xlsx"

st.set_page_config(page_title="La Valise aux Épices", page_icon="🥘", layout="centered")

# --- FONCTIONS UTILITAIRES ---
def load_menu():
    """Charge le fichier Excel s'il existe."""
    if os.path.exists(EXCEL_FILE_PATH):
        # sheet_name=None charge toutes les feuilles dans un dictionnaire
        return pd.read_excel(EXCEL_FILE_PATH, sheet_name=None)
    return None

def calculate_groceries(menu_data, selected_dishes, num_guests):
    """Calcule la liste de courses en fonction des plats choisis et du nombre de personnes."""
    shopping_list = []
    ratio = num_guests / 4.0 # Les recettes de base sont pour 4

    for dish in selected_dishes:
        df = menu_data[dish]
        for _, row in df.iterrows():
            ingredient = row['Ingrédient']
            qty = row['Quantité'] * ratio
            unit = row['Unité']
            shopping_list.append({"Plat": dish, "Ingrédient": ingredient, "Quantité": qty, "Unité": unit})
    
    # Création d'un DataFrame global
    df_shopping = pd.DataFrame(shopping_list)
    # Optionnel : On pourrait grouper par ingrédient ici pour additionner les quantités similaires
    return df_shopping

def generate_pdf(shopping_df, name, firstname):
    """Génère un PDF avec la liste de courses."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 10, txt="La Valise aux Épices", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, txt=f"Liste de courses pour {firstname} {name}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    # Grouper par plat pour un affichage joli
    for plat, group in shopping_df.groupby("Plat"):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"🍽️ {plat}", ln=True)
        pdf.set_font("Arial", size=11)
        for _, row in group.iterrows():
            texte = f"- {row['Ingrédient']} : {round(row['Quantité'], 2)} {row['Unité']}"
            pdf.cell(200, 8, txt=texte, ln=True)
        pdf.ln(5)
        
    # Sauvegarde temporaire
    pdf_filename = f"Liste_Courses_{firstname}_{name}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

def send_email(pdf_filename, name, firstname, address, phone, num_guests, selected_dishes):
    """Envoie la liste de courses par email à Lino."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"LVaE {name} {firstname}"

    body = f"""Nouvelle commande où Valou fait les courses !

Client: {firstname} {name}
Adresse: {address}
Téléphone: {phone}
Nombre de couverts: {num_guests}
Plats choisis: {', '.join(selected_dishes)}

La liste de courses est en pièce jointe.
    """
    msg.attach(MIMEText(body, 'plain'))

    # Attacher le PDF
    with open(pdf_filename, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(attach)

    # Envoi
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

# --- INTERFACE ADMIN (Cachée) ---
with st.sidebar:
    st.markdown("### 🔒 Accès Admin")
    admin_input = st.text_input("Mot de passe", type="password")
    
    if admin_input == ADMIN_PASSWORD:
        st.success("Mode Admin activé")
        uploaded_file = st.file_uploader("Charger le nouveau fichier Excel de plats", type=["xlsx"])
        if uploaded_file is not None:
            # On sauvegarde le fichier sur le serveur pour que les clients y aient accès
            with open(EXCEL_FILE_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Nouveau menu chargé et mis en ligne avec succès !")

# --- INTERFACE CLIENT ---
st.title("🥘 La Valise aux Épices")
st.write("Bienvenue ! Configurez votre repas et laissez-vous guider.")

menu_data = load_menu()

if menu_data is None:
    st.info("Notre menu est en cours de mise à jour. Revenez très vite !")
else:
    available_dishes = list(menu_data.keys())
    
    with st.form("client_form"):
        st.subheader("Vos informations")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom", required=True)
            firstname = st.text_input("Prénom", required=True)
        with col2:
            phone = st.text_input("Téléphone", value="+33 ", required=True)
            address = st.text_input("Adresse complète", required=True)
            
        st.subheader("Votre Repas")
        num_guests = st.selectbox("Pour combien de personnes ?", options=list(range(1, 21)), index=3) # Par défaut 4
        
        selected_dishes = st.multiselect(
            "Choisissez vos plats (jusqu'à 5)", 
            options=available_dishes,
            max_selections=5
        )
        
        st.subheader("Les Courses")
        course_option = st.radio(
            "Comment souhaitez-vous gérer les courses ?",
            options=["Je fais les courses moi-même", "Valou fait les courses (+15€)"]
        )
        
        submitted = st.form_submit_button("Valider la commande")
        
    if submitted:
        if not selected_dishes:
            st.error("Veuillez sélectionner au moins un plat.")
        elif not name or not firstname or not address:
            st.error("Veuillez remplir toutes vos informations (Nom, Prénom, Adresse).")
        else:
            st.success("Commande validée ! Traitement en cours...")
            
            # Calcul des courses
            shopping_df = calculate_groceries(menu_data, selected_dishes, num_guests)
            pdf_path = generate_pdf(shopping_df, name, firstname)
            
            if course_option == "Je fais les courses moi-même":
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Télécharger votre liste de courses (PDF)",
                        data=f,
                        file_name=f"La_Valise_aux_Epices_Courses_{firstname}.pdf",
                        mime="application/pdf"
                    )
            else: # Valou fait les courses
                if send_email(pdf_path, name, firstname, address, phone, num_guests, selected_dishes):
                    st.success("Votre demande a été envoyée à Valou ! Vous n'avez plus rien à faire.")
            
            # Nettoyage du fichier PDF temporaire
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
