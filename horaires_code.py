import streamlit as st
import requests
import re

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Horaires Lausanne", page_icon="🕌", layout="centered")

# --- TITRE ET EN-TÊTE ---
st.title("🕌 Horaires de Précaution")
st.markdown("**Agglomération Lausannoise** - Horaires de prière")
st.divider()

# --- DONNÉES ET LISTES ---
mosques = ["Al-Taqwa", "CCML", "Omar Crissier", "Bukhari", "Assalam", "Alhikma"]
urls = [
    "https://mawaqit.net/fr/association-al-taqwa-lausanne-1018-switzerland-1",
    "https://mawaqit.net/fr/ccml",
    "https://mawaqit.net/fr/omar-crissier",
    "https://mawaqit.net/fr/alboukhari-lausanne",
    "https://mawaqit.net/fr/assala-lausanne",
    "https://mawaqit.net/fr/alhikma-lausanne"
]

fajr_compare, duhr_compare, asr_compare, maghrib_compare, icha_compare = [], [], [], [], []

# --- EXTRACTION DES DONNÉES (avec barre de chargement) ---
with st.spinner("Récupération des horaires en cours..."):
    for url in urls:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            match = re.search(r'"times":\[(.*?)\]', response.text)
            if match:
                horaires_bruts = match.group(1).replace('"', '').split(',')
                fajr_compare.append(horaires_bruts[0])
                duhr_compare.append(horaires_bruts[1])
                asr_compare.append(horaires_bruts[2])
                maghrib_compare.append(horaires_bruts[3])
                icha_compare.append(horaires_bruts[4])
    icha_compare.pop(1)

# --- CALCULS DE PRÉCAUTION ---
if fajr_compare: # Si la liste n'est pas vide
    imsak = min(fajr_compare)
    fajr = max(fajr_compare)
    duhr = max(duhr_compare)
    asr = max(asr_compare)
    maghrib = max(maghrib_compare)
    icha = max(icha_compare)

    # --- AFFICHAGE DE L'INTERFACE ---
    
   
    st.error(f"🛑 **IMSAK (Arrêt de la nourriture) : {imsak}**")
    st.info(f"🌅 **FAJR (Heure de prière sûre) : {fajr}**")
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="☀️ Dhuhr", value=duhr)
    with col2:
        st.metric(label="🌤️ Asr", value=asr)
    with col3:
        st.metric(label="🍲 Maghrib (Iftar)", value=maghrib)
    with col4 :
         st.metric(label="🌙 Isha", value=icha)
        
    st.divider()

    
    # --- DÉTAILS TRANPARENTS ---
    with st.expander("Voir les mosquées scannées"):
        for m in mosques:
            st.write(f"- {m}")
else:

    st.error("Impossible de récupérer les données aujourd'hui.")

