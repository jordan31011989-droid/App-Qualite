import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURATION ET DESIGN ---
st.set_page_config(page_title="SMP Sentinel Py", layout="wide", page_icon="🛡️")

# Injection de CSS pour le "Graphic Design"
st.markdown("""
    <style>
    /* Couleur de fond de l'appli */
    .stApp { background-color: #F1F5F9; }
    
    /* Design des titres */
    h1, h2, h3 { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Style du bouton de validation */
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white; font-size: 18px; font-weight: bold; 
        border-radius: 12px; height: 3.5em; border: none;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }
    
    /* Style pour les blocs de questions */
    div[data-testid="stForm"] {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-top: 5px solid #3B82F6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_ready = True
except:
    sheet_ready = False

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=180)
    st.markdown("---")
    st.markdown("### 👤 **Garant Qualité**")
    menu = st.radio("Navigation", 
                    ["📋 Checklist Terrain", "📦 Audit Produits Finis", "🔧 Demandes Opérateurs", "📊 Dashboard Stats"],
                    label_visibility="collapsed")
    st.divider()
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y - %H:%M')}")

# ==========================================
# 1. CHECKLIST TERRAIN (VERSION DESIGN & JAUGES)
# ==========================================
if menu == "📋 Checklist Terrain":
    
    st.markdown("<h1>📋 Checklist Terrain</h1>", unsafe_allow_html=True)
    st.write("Sélectionnez le secteur puis évaluez chaque critère en glissant la jauge.")
    
    # LE CHOIX DU SECTEUR EST DEHORS POUR METTRE À JOUR EN DIRECT
    c1, c2 = st.columns([1, 2])
    with c1:
        secteur = st.selectbox("📍 CHOIX DU SECTEUR", ["Débit", "Sertissage/Jointage", "Montage", "Usinage", "Logistique/Expédition"])
    
    # Points de contrôle réécrits de façon professionnelle
    criteres_par_secteur = {
        "Débit": [
            "🧹 Propreté et rangement du poste", 
            "📏 Suivi dimensionnel des profils", 
            "🛡️ Aspect visuel (Absence de coups/griffes)", 
            "💧 Conformité du drainage traverse", 
            "✂️ Qualité des coupes et absence de bavures"
        ],
        "Sertissage/Jointage": [
            "💧 Pulvérisation H2O conforme", 
            "🔧 Sertissage (Absence de jeu)", 
            "🛡️ Étanchéité des dormants", 
            "✨ Propreté des cadres (sans traces)", 
            "📐 Contrôle de l'équerrage"
        ],
        "Montage": ["Cales vitrage", "Serrage paumelles", "Test ouverture/fermeture", "Fixation crémones", "Défauts d'aspect"],
        "Usinage": ["Conformité perçages", "Ébavurage", "Évacuation copeaux", "Contrôle dimensionnel"],
        "Logistique/Expédition": ["État palette", "Calage et moussage", "Étiquetage", "Fixation colis"]
    }

    st.markdown("<br>", unsafe_allow_html=True)

    # --- LE FORMULAIRE ---
    with st.form("audit_form"):
        st.markdown(f"### 🔍 Évaluation : {secteur}")
        st.markdown("---")
        
        resultats_audit = {}
        
        # Affichage des jauges (select_slider)
        for question in criteres_par_secteur[secteur]:
            st.markdown(f"**{question}**")
            # La fameuse jauge ultra visuelle
            resultats_audit[question] = st.select_slider(
                label="Évaluation", # Caché visuellement mais nécessaire
                options=["❌ Non Conforme", "⚠️ Vigilance", "✅ Conforme"],
                value="✅ Conforme",
                label_visibility="collapsed"
            )
            st.markdown("<br>", unsafe_allow_html=True) # Espace entre chaque question
            
        st.markdown("---")
        st.markdown("### ✍️ Rapport de l'auditeur")
        obs = st.text_area("Observations, remarques ou actions correctives immédiates :", placeholder="Tout est conforme sur ce poste...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 VALIDER ET TRANSMETTRE L'AUDIT")
        
        if submit:
            details_str = " | ".join([f"{k}: {v}" for k, v in resultats_audit.items()])
            nb_nok = list(resultats_audit.values()).count("❌ Non Conforme")
            etat = "NOK" if nb_nok > 0 else "OK"
            
            data_to_save = {
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "Type": "Checklist", 
                "Secteur": secteur, 
                "Machine_Ref": "N/A", 
                "Conformite": etat, 
                "Details_Audit": details_str, 
                "Observations": obs
            }
            
            if sheet_ready:
                try:
                    df = conn.read()
                    df = pd.concat([df, pd.DataFrame([data_to_save])], ignore_index=True)
                    conn.update(data=df)
                    st.balloons()
                    st.success(f"✅ L'audit du secteur **{secteur}** a été enregistré avec succès !")
                except Exception as e: 
                    st.error(f"Erreur d'envoi : {e}")
            else:
                st.warning("⚠️ Non envoyé : Connectez votre Google Sheets dans les 'Secrets'.")

# ==========================================
# (Menus basiques pour l'instant)
# ==========================================
elif menu == "📦 Audit Produits Finis":
    st.title("📦 Audit Produits Finis")
    st.info("Section en cours de design...")

elif menu == "🔧 Demandes Opérateurs":
    st.title("🔧 Demandes Opérateurs")
    st.info("Section en cours de design...")

elif menu == "📊 Dashboard Stats":
    st.title("📊 Dashboard Stats")
    if sheet_ready:
        try:
            st.dataframe(conn.read())
        except:
            st.warning("Connectez Google Sheets.")
