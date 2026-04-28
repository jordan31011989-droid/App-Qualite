import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from datetime import datetime
import plotly.express as px

# --- DESIGN PREMIUM ---
st.set_page_config(page_title="SMP Sentinel Pro", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .main-title { color: #1E3A8A; font-size: 28px; font-weight: bold; margin-bottom: 15px; }
    .stButton>button { background: linear-gradient(to right, #074799, #001A6E); color: white; border-radius: 8px; font-weight: bold; border: none; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_ready = True
except:
    sheet_ready = False

# --- MENU LATÉRAL ---
with st.sidebar:
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=150)
    menu = st.radio("MENU", ["📋 Checklist Terrain", "📦 Produits Finis", "🛠️ Demandes Opérateurs", "📊 Dashboard"])
    st.divider()
    st.caption("Garant Qualité - SMP")

# --- FONCTION PDF ---
def export_pdf(title, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"RAPPORT : {title}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for k, v in data.items():
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(50, 8, f" {k}", border=1, fill=True)
        pdf.multi_cell(140, 8, f" {v}", border=1)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 1. CHECKLIST TERRAIN (AVEC TES VRAIS CRITÈRES)
# ==========================================
if menu == "📋 Checklist Terrain":
    st.markdown('<p class="main-title">📋 Checklist Terrain</p>', unsafe_allow_html=True)
    
    # Tes vraies données issues de tes fichiers
    criteres_par_secteur = {
        "Débit": ["Propreté du poste de travail", "Port des EPI", "Évacuation des chutes", "Rangement de la zone", "Qualité des coupes (absence de bavures)", "Précision dimensionnelle des profils"],
        "Sertissage/Jointage": ["Application correcte de la colle/silicone", "Qualité de l'assemblage (pas de jour)", "Mise en place des joints (sans étirement)", "Propreté des cadres (pas de traces de colle)", "Contrôle de l'équerrage"],
        "Montage": ["Mise en place des cales vitrage", "Serrage correct des paumelles/charnières", "Test de fonctionnement (ouverture/fermeture fluide)", "Fixation des crémones et gâches", "Absence de rayures/défauts d'aspect"],
        "Usinage": ["Conformité des perçages et fraisages", "Ébavurage correct", "Évacuation des copeaux", "Contrôle dimensionnel après usinage"],
        "Logistique/Expédition": ["Qualité de l'emballage (film, cales)", "Étiquetage conforme", "Conditionnement sur palette (stabilité)", "Vérification des accessoires joints à la commande"]
    }
    
    with st.form("form_checklist"):
        c1, c2 = st.columns(2)
        with c1: secteur = st.selectbox("📍 Secteur", list(criteres_par_secteur.keys()))
        with c2: machine = st.text_input("⚙️ Machine / Ligne", "Poste Principal")
        
        st.markdown("### 🔍 Points de contrôle")
        resultats_audit = {}
        
        # Affiche les questions spécifiques au secteur choisi
        for question in criteres_par_secteur[secteur]:
            resultats_audit[question] = st.radio(f"**{question}**", ["Conforme", "Mineur", "Majeur"], horizontal=True)
            
        obs = st.text_area("✍️ Observations")
        submit = st.form_submit_button("VALIDER L'AUDIT")
        
        if submit:
            # Calcul de conformité basique
            nb_majeur = list(resultats_audit.values()).count("Majeur")
            etat = "NOK" if nb_majeur > 0 else "OK"
            
            # Formatage des détails pour Google Sheets
            details_str = " | ".join([f"{k}: {v}" for k, v in resultats_audit.items()])
            
            data_to_save = {"Date": datetime.now().strftime("%d/%m/%Y %H:%M"), "Type": "Checklist", "Secteur": secteur, "Machine_Ref": machine, "Conformite": etat, "Details_Audit": details_str, "Observations": obs}
            
            if sheet_ready:
                try:
                    df = conn.read()
                    df = pd.concat([df, pd.DataFrame([data_to_save])], ignore_index=True)
                    conn.update(data=df)
                    st.success("✅ Audit enregistré !")
                    st.download_button("📩 Télécharger le PDF", export_pdf(f"Audit {secteur}", data_to_save), f"Audit_{secteur}.pdf")
                except Exception as e: st.error(f"Erreur Google Sheets : {e}")

# ==========================================
# 2. PRODUITS FINIS (TES VRAIS CRITÈRES)
# ==========================================
elif menu == "📦 Produits Finis":
    st.markdown('<p class="main-title">📦 Audit Produits Finis</p>', unsafe_allow_html=True)
    
    pf_criteres = [
        "Châssis bien positionné sur la palette", "Calage adéquat entre les menuiseries",
        "Fixation sécurisée par sangle/film", "Étiquetage client clair et visible",
        "Présence du colis d'accessoires (si applicable)", "Menuiseries sans rayures/salissures",
        "Contrôle global de la géométrie avant expédition"
    ]
    
    with st.form("form_pf"):
        ref = st.text_input("🆔 Référence Commande / Palette")
        scores = {}
        st.markdown("### Évaluation")
        for crit in pf_criteres:
            scores[crit] = st.select_slider(f"{crit}", options=["NOK", "OK"], value="OK")
            
        obs = st.text_area("Observations")
        if st.form_submit_button("ENREGISTRER PRODUIT FINI"):
            nb_nok = list(scores.values()).count("NOK")
            etat = "CONFORME" if nb_nok == 0 else "NON CONFORME"
            details_str = " | ".join([f"{k}: {v}" for k, v in scores.items()])
            
            data_to_save = {"Date": datetime.now().strftime("%d/%m/%Y %H:%M"), "Type": "Produit Fini", "Secteur": "Expédition", "Machine_Ref": ref, "Conformite": etat, "Details_Audit": details_str, "Observations": obs}
            
            if sheet_ready:
                try:
                    df = conn.read()
                    df = pd.concat([df, pd.DataFrame([data_to_save])], ignore_index=True)
                    conn.update(data=df)
                    if etat == "CONFORME": st.success("✅ Produit conforme, enregistré !")
                    else: st.error("❌ Produit Non Conforme, enregistré !")
                except: st.error("Erreur Google Sheets")

# ==========================================
# 3. DEMANDES OPÉRATEURS (TON FICHIER EXACT)
# ==========================================
elif menu == "🛠️ Demandes Opérateurs":
    st.markdown('<p class="main-title">🛠️ Saisie Demande Opérateur</p>', unsafe_allow_html=True)
    
    with st.form("form_demande"):
        c1, c2 = st.columns(2)
        with c1: secteur = st.selectbox("Secteur", ["Débit", "Sertissage/Jointage", "Montage", "Usinage", "Logistique/Expédition"])
        with c2: machine = st.text_input("Machine / Poste")
        
        desc = st.text_area("Description du problème")
        crit = st.select_slider("Criticité", options=["Basse", "Moyenne", "Haute"])
        statut = st.radio("État d'avancement", ["À faire", "En cours", "Terminé"], horizontal=True)
        
        if st.form_submit_button("ENVOYER DEMANDE"):
            details_str = f"Criticité: {crit} | Statut: {statut}"
            data_to_save = {"Date": datetime.now().strftime("%d/%m/%Y %H:%M"), "Type": "Demande", "Secteur": secteur, "Machine_Ref": machine, "Conformite": statut, "Details_Audit": details_str, "Observations": desc}
            
            if sheet_ready:
                try:
                    df = conn.read()
                    df = pd.concat([df, pd.DataFrame([data_to_save])], ignore_index=True)
                    conn.update(data=df)
                    st.success("✅ Demande transmise !")
                except: st.error("Erreur Google Sheets")

# ==========================================
# 4. DASHBOARD STATS
# ==========================================
elif menu == "📊 Dashboard":
    st.markdown('<p class="main-title">📊 Historique & Dashboard</p>', unsafe_allow_html=True)
    
    if sheet_ready:
        try:
            df = conn.read()
            if not df.empty:
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)
                
                # Petit graphique rapide
                df_audits = df[df['Type'].isin(['Checklist', 'Produit Fini'])]
                if not df_audits.empty:
                    st.subheader("Bilan des conformités")
                    fig = px.pie(df_audits, names='Conformite', color='Conformite', color_discrete_map={"OK": "green", "CONFORME": "green", "NOK": "red", "NON CONFORME": "red"})
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée enregistrée pour le moment.")
        except:
            st.warning("Vérifiez la connexion Google Sheets.")
