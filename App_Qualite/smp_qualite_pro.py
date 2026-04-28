import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from fpdf import FPDF # Assurez-vous d'avoir fpdf2 dans votre requirements.txt

# --- CONFIGURATION ---
st.set_page_config(page_title="SMP Sentinel Py", layout="wide", page_icon="🛡️")

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_ready = True
except:
    sheet_ready = False

# --- FONCTION PDF (CORRIGÉE) ---
def export_pdf(title, data_dict):
    pdf = FPDF()
    pdf.add_page()
    
    # Titre du rapport
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(190, 10, txt=title.upper(), ln=True, align='C')
    pdf.ln(10)
    
    # Contenu du rapport
    pdf.set_font("helvetica", size=11)
    for key, value in data_dict.items():
        # Nettoyage des caractères spéciaux pour éviter les bugs
        clean_key = str(key).encode('latin-1', 'replace').decode('latin-1')
        clean_val = str(value).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(60, 10, txt=f" {clean_key}", border=1, fill=True)
        pdf.cell(130, 10, txt=f" {clean_val}", border=1, ln=True)
        
    # Retourne les bytes directement (syntaxe fpdf2)
    return pdf.output()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=150)
    menu = st.radio("Navigation", ["📋 Checklist Terrain", "📊 Dashboard Stats"])

if menu == "📋 Checklist Terrain":
    st.title("📋 Checklist Terrain")
    
    secteur = st.selectbox("Secteur d'audit", ["Débit", "Sertissage", "Montage", "Usinage", "Expédition"])
    
    criteres = {
        "Débit": ["Propreté poste", "Suivis dimensionnels", "Coups et griffes", "Drainage traverse", "Coupes et bavures"],
        "Sertissage": ["Pulvérisation H2O", "Sertissage sans jeu", "Étanchéité dormants", "Propreté cadres", "Équerrage"]
    }
    
    questions = criteres.get(secteur, ["Contrôle général"])

    with st.form("audit_form"):
        st.markdown(f"### Audit : {secteur}")
        resultats = {}
        
        # On affiche les questions proprement
        for q in questions:
            resultats[q] = st.radio(f"**{q}**", ["OK", "Vig", "NOK"], horizontal=True)
            
        obs = st.text_area("Observations")
        submit = st.form_submit_button("VALIDER ET GÉNÉRER PDF")
        
        if submit:
            # Préparation des données
            data_save = {
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Secteur": secteur,
                "Etat": "OK" if "NOK" not in resultats.values() else "NOK",
                "Observations": obs
            }
            
            # 1. Sauvegarde Google Sheets
            if sheet_ready:
                try:
                    df = conn.read()
                    df = pd.concat([df, pd.DataFrame([data_save])], ignore_index=True)
                    conn.update(data=df)
                    st.success("✅ Enregistré dans Google Sheets !")
                except:
                    st.warning("⚠️ Sauvegarde Sheets impossible.")

            # 2. Génération et téléchargement du PDF
            try:
                # On ajoute les détails des questions au dictionnaire pour le PDF
                data_pdf = {**data_save, **resultats}
                pdf_bytes = export_pdf(f"Audit {secteur}", data_pdf)
                
                st.download_button(
                    label="📥 Télécharger le Rapport PDF",
                    data=pdf_bytes,
                    file_name=f"Audit_{secteur}_{datetime.now().strftime('%d%m_%H%M')}.pdf",
                    mime="application/pdf"
                )
                st.balloons()
            except Exception as e:
                st.error(f"Erreur PDF : {e}")

elif menu == "📊 Dashboard Stats":
    st.title("📊 Dashboard")
    if sheet_ready:
        st.dataframe(conn.read())
