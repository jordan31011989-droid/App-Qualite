import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="SMP Sentinel Pro", layout="wide", page_icon="🛡️")

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Liaison Google Sheets non configurée dans les Secrets.")

# --- BARRE LATÉRALE / MENU ---
st.sidebar.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=150) # Optionnel : mettez votre logo
st.sidebar.title("MENU PRINCIPAL")
page = st.sidebar.radio("Navigation", 
    ["📋 Checklist Terrain", "📦 Audit Produits Finis", "🔧 Demandes Opérateurs", "📊 Dashboard Stats"])

# --- FONCTION PDF ---
def generate_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "RAPPORT D'AUDIT QUALITE - SMP", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for key, value in data_dict.items():
        pdf.cell(100, 10, f"{key}: {value}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- PAGE 1 : CHECKLIST TERRAIN ---
if page == "📋 Checklist Terrain":
    st.header("📋 Checklist Terrain")
    
    with st.form("form_checklist"):
        auditeur = st.text_input("Auditeur", "Jordan")
        secteur = st.selectbox("Secteur", ["Débit", "Usinage", "Montage", "Expédition"])
        
        st.divider()
        c1 = st.radio("Propreté du poste", ["OK", "Vig", "NOK"], horizontal=True)
        c2 = st.radio("Suivis dimensionnels", ["OK", "Vig", "NOK"], horizontal=True)
        c3 = st.radio("Coups et griffes", ["OK", "Vig", "NOK"], horizontal=True)
        obs = st.text_area("Observations")
        
        submitted = st.form_submit_button("ENREGISTRER L'AUDIT")
        
        if submitted:
            data = {
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Utilisateur": auditeur,
                "Secteur": secteur,
                "Proprete": c1,
                "Dimensionnel": c2,
                "Coups_Griffes": c3,
                "Observations": obs
            }
            # Envoi Google Sheets
            df_new = pd.DataFrame([data])
            existing_df = conn.read()
            updated_df = pd.concat([existing_df, df_new], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ Enregistré dans Google Sheets !")
            
            # Bouton PDF qui apparaît après validation
            st.download_button("📥 Télécharger le Rapport PDF", 
                             data=generate_pdf(data), 
                             file_name=f"Audit_{secteur}.pdf")

# --- PAGE 2 : AUDIT PRODUITS FINIS ---
elif page == "📦 Audit Produits Finis":
    st.header("📦 Audit Produits Finis")
    st.info("Espace dédié au contrôle final avant expédition.")
    # Ajoutez ici vos champs spécifiques pour les produits finis

# --- PAGE 3 : DEMANDES OPÉRATEURS ---
elif page == "🔧 Demandes Opérateurs":
    st.header("🔧 Demandes Opérateurs")
    st.write("Gestion des demandes et alertes terrain.")
    # Ajoutez ici vos champs pour les demandes opérateurs

# --- PAGE 4 : DASHBOARD STATS ---
elif page == "📊 Dashboard Stats":
    st.header("📊 Tableau de Bord")
    try:
        df = conn.read()
        st.dataframe(df) # Affiche votre Google Sheet en direct
        
        # Petit graphique d'exemple
        if not df.empty:
            st.bar_chart(df['Secteur'].value_counts())
    except:
        st.warning("Aucune donnée à afficher pour le moment.")
