import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="SMP Sentinel Pro", layout="wide")

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🛡️ SMP Sentinel - Audit & Reporting")

# --- FORMULAIRE D'AUDIT ---
with st.form("audit_form"):
    st.subheader("📝 Nouvel Audit Terrain")
    
    col1, col2 = st.columns(2)
    with col1:
        auditeur = st.text_input("Nom de l'auditeur", "Jordan")
        secteur = st.selectbox("Secteur", ["Débit", "Usinage", "Montage", "Expédition"])
    
    st.divider()
    
    # Critères
    c1 = st.radio("Propreté du poste", ["OK", "Vig", "NOK"], horizontal=True)
    c2 = st.radio("Suivis dimensionnels", ["OK", "Vig", "NOK"], horizontal=True)
    c3 = st.radio("Coups et griffes", ["OK", "Vig", "NOK"], horizontal=True)
    
    obs = st.text_area("Commentaires / Observations")
    
    submitted = st.form_submit_button("ENREGISTRER DANS GOOGLE SHEETS")

    if submitted:
        # Préparation des données
        nouveaux_points = pd.DataFrame([{
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Utilisateur": auditeur,
            "Secteur": secteur,
            "Proprete": c1,
            "Dimensionnel": c2,
            "Coups_Griffes": c3,
            "Observations": obs
        }])
        
        # Envoi vers Google Sheets
        try:
            existing_data = conn.read()
            updated_df = pd.concat([existing_data, nouveaux_points], ignore_index=True)
            conn.update(data=updated_df)
            st.success("✅ Audit enregistré avec succès dans Google Sheets !")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

# --- BOUTON RAPPORT PDF ---
st.sidebar.header("📥 Export")
if st.sidebar.button("Générer Rapport PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "RAPPORT D'AUDIT QUALITE - SMP", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    pdf.cell(100, 10, f"Auditeur: {auditeur}", ln=True)
    pdf.cell(100, 10, f"Secteur: {secteur}", ln=True)
    pdf.ln(5)
    pdf.cell(100, 10, f"Proprete: {c1}", ln=True)
    pdf.cell(100, 10, f"Dimensionnel: {c2}", ln=True)
    pdf.cell(100, 10, f"Observations: {obs}", ln=True)
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    st.sidebar.download_button(
        label="⬇️ Télécharger le PDF",
        data=pdf_output,
        file_name=f"Audit_{secteur}_{datetime.now().strftime('%H%M')}.pdf",
        mime="application/pdf"
    )
