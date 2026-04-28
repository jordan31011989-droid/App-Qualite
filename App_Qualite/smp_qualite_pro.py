import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="SMP Sentinel Py", layout="wide", page_icon="🛡️")

# --- CONNEXION GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_ready = True
except:
    sheet_ready = False

# --- BARRE LATÉRALE (Exactement comme ton image) ---
with st.sidebar:
    st.markdown("## 🛡️ SMP Sentinel Py")
    st.write("Utilisateur : **Garant Qualité**")
    st.divider()
    
    st.write("Menu Principal")
    menu = st.radio("Navigation", 
                    ["📋 Checklist Terrain", "📦 Audit Produits Finis", "🔧 Demandes Opérateurs", "📊 Dashboard Stats"],
                    label_visibility="collapsed")
    
    st.divider()
    st.info(f"Dernière synchro : {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 1. CHECKLIST TERRAIN (Le correctif est ici)
# ==========================================
if menu == "📋 Checklist Terrain":
    
    st.title("📋 Checklist Terrain")
    
    # ⚠️ LE CHOIX DU SECTEUR EST EN DEHORS DU FORMULAIRE POUR CHANGER EN DIRECT ⚠️
    secteur = st.selectbox("Secteur d'audit", ["Débit", "Sertissage/Jointage", "Montage", "Usinage", "Logistique/Expédition"])
    
    # Les questions par secteur (j'ai repris tes mots exacts pour le Débit)
    criteres_par_secteur = {
        "Débit": [
            "Propreté poste", 
            "Suivis dimensionnels", 
            "Coups et griffes", 
            "Drainage traverse", 
            "Coupes et bavures"
        ],
        "Sertissage/Jointage": ["Pulvérisation H2O", "Sertissage sans jeu", "Étanchéité dormants", "Propreté cadres", "Équerrage"],
        "Montage": ["Cales vitrage", "Serrage paumelles", "Test ouverture/fermeture", "Fixation crémones", "Défauts d'aspect"],
        "Usinage": ["Conformité perçages", "Ébavurage", "Évacuation copeaux", "Contrôle dimensionnel"],
        "Logistique/Expédition": ["État palette", "Calage et moussage", "Étiquetage", "Fixation colis"]
    }

    # --- LE FORMULAIRE COMMENCE ICI ---
    with st.form("audit_form"):
        resultats_audit = {}
        
        # On affiche les questions qui correspondent au secteur sélectionné au-dessus
        for question in criteres_par_secteur[secteur]:
            resultats_audit[question] = st.radio(question, ["OK", "Vig", "NOK"], horizontal=True)
            
        obs = st.text_area("Commentaires / Observations")
        
        # Le bouton de validation
        submit = st.form_submit_button("ENREGISTRER L'AUDIT")
        
        if submit:
            # On prépare les données pour Google Sheets
            details_str = " | ".join([f"{k}: {v}" for k, v in resultats_audit.items()])
            nb_nok = list(resultats_audit.values()).count("NOK")
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
                    st.success("✅ Audit enregistré dans Google Sheets avec succès !")
                except Exception as e: 
                    st.error(f"Erreur d'envoi vers Google Sheets.")
            else:
                st.warning("⚠️ L'envoi n'a pas pu se faire : Connexion Google Sheets manquante (Étape 2).")

# ==========================================
# (Les autres menus restent simples en attendant)
# ==========================================
elif menu == "📦 Audit Produits Finis":
    st.title("📦 Audit Produits Finis")
    st.info("Section en construction...")

elif menu == "🔧 Demandes Opérateurs":
    st.title("🔧 Demandes Opérateurs")
    st.info("Section en construction...")

elif menu == "📊 Dashboard Stats":
    st.title("📊 Dashboard Stats")
    if sheet_ready:
        try:
            df = conn.read()
            st.dataframe(df)
        except:
            st.warning("Connectez Google Sheets pour voir les données.")
