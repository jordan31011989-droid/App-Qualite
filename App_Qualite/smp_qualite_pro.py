import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import plotly.express as px

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="SMP Sentinel Pro", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    h1, h2, h3 { color: #1E3A8A; }
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white; border-radius: 10px; height: 3.5em; border: none; width: 100%;
    }
    div[data-testid="stForm"] {
        background-color: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-top: 4px solid #1E3A8A;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_ready = True
except:
    sheet_ready = False

# --- MENU ---
with st.sidebar:
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=160)
    menu = st.radio("MENU", ["📋 Checklist Terrain", "📦 Produits Finis", "🔧 Demandes", "📊 Dashboard Stats"])

# --- DONNÉES DES SECTEURS ---
criteres = {
    "Débit": ["Propreté poste", "Suivis dimensionnels", "Coups et griffes", "Drainage traverse", "Coupes et bavures"],
    "Usinage": ["Conformité perçages", "Ébavurage", "Évacuation copeaux", "Contrôle dimensionnel"],
    "Sertissage": ["Pulvérisation H2O", "Sertissage sans jeu", "Étanchéité dormants", "Propreté cadres", "Équerrage"],
    "Ferrage": ["Position gâches", "Vissage paumelles", "Alignement quincaillerie", "Graissage", "Rayures"],
    "Montage": ["Test d'eau", "Étanchéité appui", "Fonctionnement ouv/ferm", "Fixation crémones"],
    "Vitrage": ["Propreté verres", "Position cales", "Pose parcloses", "Joint vitrage"],
    "Expédition": ["État palette", "Moussage", "Étiquetage", "Fixation colis"]
}

# ==========================================
# 1. CHECKLIST TERRAIN
# ==========================================
if menu == "📋 Checklist Terrain":
    st.title("📋 Checklist Terrain")
    secteur = st.selectbox("📍 CHOIX DU SECTEUR", list(criteres.keys()))

    with st.form("audit_form"):
        st.markdown(f"### Évaluation : {secteur}")
        results = {}
        for q in criteres[secteur]:
            results[q] = st.radio(f"**{q}**", ["🟢 OK", "🟠 VIG", "🔴 NOK"], horizontal=True)
        
        obs = st.text_area("Observations")
        if st.form_submit_button("🚀 VALIDER ET TRANSMETTRE"):
            # Préparation des données
            nb_nok = list(results.values()).count("🔴 NOK")
            etat = "NOK" if nb_nok > 0 else "OK"
            details = " | ".join([f"{k}: {v}" for k, v in results.items()])
            
            new_row = {
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Type": "Checklist",
                "Secteur": secteur,
                "Conformite": etat,
                "Details": details,
                "Observations": obs
            }
            
            if sheet_ready:
                try:
                    df_existing = conn.read()
                    df_updated = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
                    # FIX DE L'ERREUR : On convertit en liste de dictionnaires
                    conn.update(data=df_updated.to_dict(orient="records"))
                    st.balloons()
                    st.success("✅ Données envoyées !")
                except Exception as e:
                    st.error(f"Erreur : {e}")

# ==========================================
# 4. DASHBOARD STATS (GRAPHIQUES AUTOMATIQUES)
# ==========================================
elif menu == "📊 Dashboard Stats":
    st.title("📊 Statistiques en Temps Réel")
    
    if sheet_ready:
        df = conn.read()
        if not df.empty:
            # Métriques
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Audits", len(df))
            col2.metric("Taux OK", f"{(len(df[df['Conformite']=='OK'])/len(df)*100):.1f}%")
            col3.metric("Alertes NOK", len(df[df['Conformite']=='NOK']))

            st.divider()

            # Graphiques
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Audits par Secteur")
                fig_bar = px.bar(df['Secteur'].value_counts(), labels={'value':'Nombre', 'index':'Secteur'}, color_discrete_sequence=['#1E3A8A'])
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with g2:
                st.subheader("Répartition Conformité")
                fig_pie = px.pie(df, names='Conformite', color='Conformite', color_discrete_map={'OK':'#2ecc71', 'NOK':'#e74c3c'})
                st.plotly_chart(fig_pie, use_container_width=True)

            st.subheader("Historique des données")
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("Aucune donnée disponible.")
