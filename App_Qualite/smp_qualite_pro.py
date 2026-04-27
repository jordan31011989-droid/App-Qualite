import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import datetime
import plotly.express as px

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="SMP Sentinel Elite", layout="wide", page_icon="🛡️")

# --- STYLE CSS PERSONNALISÉ (Le "Secret" pour que ça cartonne) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #F0F2F6; }
    
    /* Style des blocs (Cartes) */
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-image: linear-gradient(to right, #0052D4, #4364F7, #6FB1FC);
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    
    /* Titres */
    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION LATÉRALE ---
with st.sidebar:
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=180)
    st.markdown("### 👤 **Session: Jordan**")
    st.caption("Garant Qualité - Niveau Administrateur")
    st.divider()
    
    menu = st.radio("TABLEAU DE BORD", 
        ["🚀 Lancer un Audit", "📈 Statistiques Live", "📁 Historique Complet"],
        index=0)
    
    st.divider()
    if st.button("🔄 Actualiser les données"):
        st.rerun()

# --- FONCTION GENERATION PDF ---
def export_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 58, 138) # Bleu SMP
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 25, "RAPPORT D'AUDIT QUALITE SMP", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    for key, value in data.items():
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(60, 10, f" {key}", border=1, fill=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(130, 10, f" {value}", border=1, ln=True)
        pdf.set_font("Arial", 'B', 12)
        
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIQUE DES PAGES ---

if menu == "🚀 Lancer un Audit":
    st.title("🚀 Nouvel Audit Terrain")
    
    with st.container():
        with st.form("main_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                secteur = st.selectbox("📍 Secteur concerné", ["Débit", "Usinage", "Montage", "Expédition", "Logistique"])
            with c2:
                machine = st.text_input("⚙️ Machine / Poste", placeholder="Ex: Scie 01")
            
            st.markdown("---")
            st.subheader("🔍 Points de contrôle")
            
            # Grille de boutons radio
            g1, g2, g3 = st.columns(3)
            with g1:
                q1 = st.select_slider("Propreté", options=["NOK", "Vig", "OK"], value="OK")
                q2 = st.select_slider("Dimension", options=["NOK", "Vig", "OK"], value="OK")
            with g2:
                q3 = st.select_slider("Aspect", options=["NOK", "Vig", "OK"], value="OK")
                q4 = st.select_slider("Ébavurage", options=["NOK", "Vig", "OK"], value="OK")
            with g3:
                q5 = st.select_slider("Rangement", options=["NOK", "Vig", "OK"], value="OK")
            
            obs = st.text_area("✍️ Observations particulières", placeholder="RAS si tout est conforme...")
            
            submit = st.form_submit_button("VALIDER ET ENVOYER L'AUDIT")
            
            if submit:
                audit_result = {
                    "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Secteur": secteur,
                    "Machine": machine,
                    "Proprete": q1,
                    "Dimensionnel": q2,
                    "Aspect": q3,
                    "Ebavurage": q4,
                    "Rangement": q5,
                    "Observations": obs
                }
                
                try:
                    df_old = conn.read()
                    df_new = pd.concat([df_old, pd.DataFrame([audit_result])], ignore_index=True)
                    conn.update(data=df_new)
                    st.balloons()
                    st.success("🎉 Audit enregistré avec succès dans Google Sheets !")
                    
                    # Génération du PDF immédiate
                    pdf_file = export_pdf(audit_result)
                    st.download_button("📩 Télécharger le rapport (PDF)", pdf_file, f"Audit_{secteur}_{datetime.now().strftime('%d%m')}.pdf")
                except Exception as e:
                    st.error(f"Erreur technique : {e}")

elif menu == "📈 Statistiques Live":
    st.title("📈 Performance Qualité")
    
    df = conn.read()
    if not df.empty:
        # --- TOP KPI ---
        k1, k2, k3, k4 = st.columns(4)
        total = len(df)
        alertes = len(df[df.values == "NOK"])
        
        k1.metric("Total Audits", total)
        k2.metric("Alertes NOK", alertes, delta=f"-{alertes}", delta_color="inverse")
        k3.metric("Taux de Conformité", f"{int(((total-alertes)/total)*100)}%")
        k4.metric("Dernier Secteur", df['Secteur'].iloc[-1])
        
        st.divider()
        
        # --- GRAPHIQUES ---
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("📊 Volume par Secteur")
            fig_bar = px.bar(df['Secteur'].value_counts(), color_discrete_sequence=['#4364F7'])
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with g2:
            st.subheader("🎯 État Global (Aspect)")
            fig_pie = px.pie(df, names='Aspect', color='Aspect', 
                             color_discrete_map={'OK':'#2ecc71', 'Vig':'#f1c40f', 'NOK':'#e74c3c'})
            st.plotly_chart(fig_pie, use_container_width=True)
            
    else:
        st.warning("Aucune donnée disponible pour le moment.")

elif menu == "📁 Historique Complet":
    st.title("📁 Base de données Audits")
    df = conn.read()
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        # Option téléchargement Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter toute la base (CSV)", csv, "base_audits_smp.csv", "text/csv")
    else:
        st.info("L'historique est vide.")
