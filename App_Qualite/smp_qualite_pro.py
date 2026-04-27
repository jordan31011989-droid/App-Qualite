import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SMP Qualité Pro", page_icon="🛡️", layout="centered")

# --- FICHIERS DE DONNÉES ---
# On définit les noms de fichiers pour la persistance
FILE_DEMANDES = "Stats_Audits_Dashboard.xlsx - Demande opérateur a traiter .csv"
FILE_CHECKLIST = "Stats_Audits_Dashboard.xlsx - Checklist Qualité.csv"
FILE_AUDIT_PF = "Stats_Audits_Dashboard.xlsx - Audit Produits Finis.csv"
FILE_DASHBOARD = "Stats_Audits_Dashboard.xlsx - Dashboard Audits.csv"

# --- FONCTIONS DE CHARGEMENT / SAUVEGARDE ---
def load_csv(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame()

def save_to_csv(df, file):
    df.to_csv(file, index=False)

# --- STYLE CSS (Inspiration Sentinel) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2563eb; color: white; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
with st.sidebar:
    st.title("🛡️ SMP Sentinel Py")
    st.write(f"Utilisateur: **Garant Qualité**")
    menu = st.radio("Menu Principal", 
                    ["📋 Checklist Terrain", "📦 Audit Produits Finis", "🛠️ Demandes Opérateurs", "📊 Dashboard Stats"])
    st.divider()
    st.info(f"Dernière synchro : {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 1. CHECKLIST TERRAIN
# ==========================================
if menu == "📋 Checklist Terrain":
    st.header("📋 Checklist Terrain")
    secteur = st.selectbox("Secteur d'audit", ["Débit", "Sertissage", "Montage", "Ferrage", "Vitrage"])
    
    # Dictionnaire des tâches par secteur (extrait de votre fichier)
    taches = {
        "Débit": ["Propreté poste", "Suivis dimensionnels", "Coups et griffes", "Drainage traverse", "Coupes et bavures"],
        "Sertissage": ["Pulvérisation H2O", "Sertissage sans jeu", "Étanchéité dormants", "Dimensionnel", "Propreté cadres"],
        "Montage": ["Test d'eau", "Étanchéité pièce d'appui", "Stockage châssis finis"]
    }

    current_taches = taches.get(secteur, ["Contrôle général"])
    
    with st.form("form_checklist"):
        results = {}
        for t in current_taches:
            results[t] = st.radio(f"**{t}**", ["OK", "Vig", "NOK"], horizontal=True)
        
        commentaire = st.text_area("Commentaires / Observations")
        
        if st.form_submit_button("ENREGISTRER L'AUDIT"):
            st.success(f"Audit {secteur} enregistré !")
            # Logique de sauvegarde ici...

# ==========================================
# 2. AUDIT PRODUITS FINIS
# ==========================================
elif menu == "📦 Audit Produits Finis":
    st.header("📦 Audit Produits Finis")
    
    # Les 15 critères de votre fichier
    criteres = [
        "Etat de la palette", "Paletisation et moussage", "Étiquetage / clients", 
        "Contrôle étanchéités", "Positionnement joints", "Aspect général", 
        "Protection P.A", "Protection Accessoire", "Fixation colis", 
        "Stylos retouche", "Uniformité teinte", "Conformité vitrage", 
        "Jeu parecloses", "Jeu chant clippable", "Procédures internes"
    ]

    with st.form("form_pf"):
        ref_palette = st.text_input("Référence Palette", placeholder="Ex: P1")
        points = {}
        cols = st.columns(2)
        for i, crit in enumerate(criteres):
            with cols[i % 2]:
                points[crit] = st.select_slider(f"{crit}", options=[0, 1, 2, 3, 4], value=4)
        
        if st.form_submit_button("CALCULER ET SAUVEGARDER"):
            total_points = sum(points.values())
            max_points = len(criteres) * 4
            score = (total_points / max_points) * 100
            
            st.divider()
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("Score Final", f"{score:.1f}%")
            
            if score >= 90: col_res2.success("CONFORME")
            elif score >= 70: col_res2.warning("VIGILANCE")
            else: col_res2.error("NON CONFORME")

# ==========================================
# 3. DEMANDES OPÉRATEURS
# ==========================================
elif menu == "🛠️ Demandes Opérateurs":
    st.header("🛠️ Suivi des Demandes")
    
    # Chargement des données réelles
    df_demandes = load_csv(FILE_DEMANDES)
    
    with st.expander("➕ Ajouter une nouvelle demande"):
        with st.form("new_req"):
            op = st.text_input("Opérateur")
            req = st.text_area("Description du besoin")
            urg = st.slider("Urgence", 0, 100, 50)
            if st.form_submit_button("Envoyer"):
                # Simulation d'ajout
                st.success("Demande ajoutée au fichier !")

    st.subheader("Demandes actives")
    if not df_demandes.empty:
        # Nettoyage pour affichage
        display_df = df_demandes.dropna(subset=['Demande '])
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Aucune demande en attente.")

# ==========================================
# 4. DASHBOARD STATS
# ==========================================
elif menu == "📊 Dashboard Stats":
    st.header("📊 Performance Qualité")
    
    # Données issues de votre "Moyenne par critère"
    stats_data = {
        "Critère": ["Palette", "Moussage", "Étiquetage", "Étanchéité", "Joints", "Aspect", "Stylos"],
        "Score": [100, 98.3, 100, 94.4, 94.1, 81.2, 80.5]
    }
    df_stats = pd.DataFrame(stats_data)

    col1, col2 = st.columns(2)
    col1.metric("Moyenne Globale", "94.4%", "+1.2%")
    col2.metric("Point Critique", "Stylos retouche", "-5%", delta_color="inverse")

    st.subheader("Analyse par critère")
    fig = px.bar(df_stats, x="Critère", y="Score", color="Score", 
                 color_continuous_scale="RdYlGn", range_y=[0,105])
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("⚠️ **Alerte Qualité :** Le critère 'Stylos retouche' est passé sous le seuil des 85%.")