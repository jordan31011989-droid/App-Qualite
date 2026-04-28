import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURATION ET DESIGN ---
st.set_page_config(page_title="SMP Sentinel Py", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    /* Couleur de fond */
    .stApp { background-color: #F4F7F9; }
    
    /* Titres */
    h1, h2, h3 { color: #1E3A8A; font-family: 'Arial', sans-serif; }
    
    /* Bouton Valider */
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white; font-size: 18px; font-weight: bold; 
        border-radius: 10px; height: 3.5em; border: none;
        width: 100%; margin-top: 10px;
    }
    
    /* Boîte blanche du formulaire */
    div[data-testid="stForm"] {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #1E3A8A;
    }
    
    /* Espacement des boutons radio */
    div.row-widget.stRadio > div {
        gap: 30px;
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
    st.image("https://www.smp-paca.com/wp-content/uploads/2021/04/logo-smp.png", width=160)
    st.markdown("### 👤 **Garant Qualité**")
    st.divider()
    menu = st.radio("MENU", 
                    ["📋 Checklist Terrain", "📦 Audit Produits Finis", "🔧 Demandes Opérateurs", "📊 Dashboard Stats"])
    st.divider()
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

# ==========================================
# 1. CHECKLIST TERRAIN (SANS BUG)
# ==========================================
if menu == "📋 Checklist Terrain":
    
    st.markdown("<h1>📋 Checklist Terrain</h1>", unsafe_allow_html=True)
    
    # Choix du secteur (prend toute la largeur pour être bien visible)
    secteur = st.selectbox("📍 CHOIX DU SECTEUR", ["Débit", "Sertissage/Jointage", "Montage", "Usinage", "Logistique/Expédition"])
    
    # Points de contrôle pros
    criteres_par_secteur = {
        "Débit": [
            "🧹 Propreté et rangement du poste", 
            "📏 Suivi dimensionnel des profils", 
            "🛡️ Aspect visuel (Absence de coups/griffes)", 
            "💧 Conformité du drainage traverse", 
            "✂️ Qualité des coupes et absence de bavures"
        ],
        "Sertissage/Jointage": ["💧 Pulvérisation H2O conforme", "🔧 Sertissage sans jeu", "🛡️ Étanchéité dormants", "✨ Propreté des cadres", "📐 Contrôle équerrage"],
        "Montage": ["Cales vitrage", "Serrage paumelles", "Test ouverture/fermeture", "Fixation crémones", "Défauts d'aspect"],
        "Usinage": ["Conformité perçages", "Ébavurage", "Évacuation copeaux", "Contrôle dimensionnel"],
        "Logistique/Expédition": ["État palette", "Calage et moussage", "Étiquetage", "Fixation colis"]
    }

    # --- LE FORMULAIRE ---
    with st.form("audit_form"):
        st.markdown(f"### 🔍 Évaluation : {secteur}")
        st.markdown("---")
        
        resultats_audit = {}
        
        # Affichage avec des boutons simples et colorés
        for question in criteres_par_secteur[secteur]:
            resultats_audit[question] = st.radio(
                f"**{question}**", 
                options=["🟢 OK", "🟠 VIG", "🔴 NOK"], 
                horizontal=True
            )
            st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True) # Petite ligne de séparation douce
            
        st.markdown("### ✍️ Observations")
        obs = st.text_area("Remarques, actions correctives ou alertes :", placeholder="Tout est conforme...")
        
        submit = st.form_submit_button("🚀 VALIDER ET TRANSMETTRE")
        
        if submit:
            details_str = " | ".join([f"{k}: {v}" for k, v in resultats_audit.items()])
            nb_nok = list(resultats_audit.values()).count("🔴 NOK")
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
                    st.success(f"✅ Audit enregistré !")
                except Exception as e: 
                    st.error(f"Erreur d'envoi : {e}")
            else:
                st.warning("⚠️ Non envoyé : Connectez votre Google Sheets.")

# ==========================================
# (Menus basiques pour l'instant)
# ==========================================
elif menu == "📦 Audit Produits Finis":
    st.title("📦 Audit Produits Finis")
    st.info("Section en cours d'intégration...")

elif menu == "🔧 Demandes Opérateurs":
    st.title("🔧 Demandes Opérateurs")
    st.info("Section en cours d'intégration...")

elif menu == "📊 Dashboard Stats":
    st.title("📊 Dashboard Stats")
    if sheet_ready:
        try:
            st.dataframe(conn.read())
        except:
            st.warning("Connectez Google Sheets.")
