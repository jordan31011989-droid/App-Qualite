import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import datetime
import plotly.express as px

# --- DESIGN & COULEURS ---
st.set_page_config(page_title="SMP Sentinel Pro", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .main-title { color: #1E3A8A; font-size: 35px; font-weight: bold; margin-bottom: 20px; }
    .stButton>button {
        background: linear-gradient(to right, #074799, #001A6E);
        color: white; border-radius: 10px; font-weight: bold; border: none; height: 3em;
    }
    .card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS (Sécurisée) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_ready = True
except:
    sheet_ready = False

# --- MENU LATÉRAL ---
with st.sidebar:
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=150)
    st.markdown("### 🛠️ **ADMINISTRATION**")
    menu = st.radio("Navigation", ["📝 Nouvel Audit", "📊 Tableau de Bord", "📚 Historique"])
    st.divider()
    st.caption(f"Connecté : Jordan - {datetime.now().strftime('%d/%m/%Y')}")

# --- FONCTION PDF ---
def export_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "RAPPORT D'AUDIT QUALITE - SMP", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for k, v in data.items():
        pdf.cell(50, 10, f"{k} :", border=1)
        pdf.cell(130, 10, f" {v}", border=1, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIQUE DES PAGES ---

if menu == "📝 Nouvel Audit":
    st.markdown('<p class="main-title">🚀 Nouvel Audit Terrain</p>', unsafe_allow_html=True)
    
    with st.form("audit_form"):
        col1, col2 = st.columns(2)
        with col1:
            secteur = st.selectbox("📍 Secteur", ["Débit", "Usinage", "Montage", "Expédition"])
            machine = st.text_input("⚙️ Machine", "Poste 01")
        
        st.markdown("### 🔍 Contrôle")
        # On utilise des colonnes pour que ce soit beau
        q1, q2, q3 = st.columns(3)
        with q1: p1 = st.radio("Propreté", ["OK", "Vig", "NOK"], horizontal=True)
        with q2: p2 = st.radio("Dimension", ["OK", "Vig", "NOK"], horizontal=True)
        with q3: p3 = st.radio("Aspect", ["OK", "Vig", "NOK"], horizontal=True)
        
        obs = st.text_area("✍️ Observations")
        
        btn = st.form_submit_button("VALIDER L'AUDIT")
        
        if btn:
            res = {"Date": datetime.now().strftime("%d/%m/%Y %H:%M"), "Secteur": secteur, "Machine": machine, "Proprete": p1, "Dimension": p2, "Aspect": p3, "Observations": obs}
            
            if sheet_ready:
                try:
                    df = conn.read()
                    df = pd.concat([df, pd.DataFrame([res])], ignore_index=True)
                    conn.update(data=df)
                    st.balloons()
                    st.success("✅ Enregistré dans Google Sheets !")
                    st.download_button("📩 Télécharger le PDF", export_pdf(res), f"Audit_{secteur}.pdf")
                except:
                    st.error("⚠️ Erreur : Le lien Google Sheet dans 'Secrets' est absent ou mauvais.")
            else:
                st.warning("L'envoi vers Google Sheets n'est pas configuré.")

elif menu == "📊 Tableau de Bord":
    st.markdown('<p class="main-title">📊 Statistiques en Direct</p>', unsafe_allow_html=True)
    if sheet_ready:
        try:
            df = conn.read()
            if not df.empty:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Audits", len(df))
                c2.metric("Alertes NOK", len(df[df.values == "NOK"]))
                c3.metric("Dernier Audit", df['Secteur'].iloc[-1])
                
                fig = px.pie(df, names='Secteur', title="Répartition par Secteur", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Ajoutez votre lien Google Sheets pour voir les graphiques.")

elif menu == "📚 Historique":
    st.markdown('<p class="main-title">📚 Historique des Audits</p>', unsafe_allow_html=True)
    if sheet_ready:
        try:
            df = conn.read()
            st.dataframe(df, use_container_width=True)
        except:
            st.error("Lien Google Sheets manquant.")
