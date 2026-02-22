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
mosques = ["Association Al-Taqwa", "CCML", "Mosquée Omar Ibn Al Khattab Crissier", "Centre d'études islamiques Boukhari", "Centre Assalam", "Fondation Al Hikma"]
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
    with st.expander("Source des données") :
        st.markdown("""**Ce n'est en aucun cas nous qui fixons ou calculons ces horaires.** Ils sont strictement définis et mis à jour par les mosquées elles-mêmes. 
        Notre outil se contente de récupérer leurs horaires officiels (via le système Mawaqit) et d'effectuer une simple comparaison mathématique pour trouver le plus tôt et le plus tard.""")
    with st.expander("Comment ça marche ? ") :
        st.markdown("""
Face à la diversité des méthodes de calcul (degrés d'inclinaison du soleil) utilisées par les différentes mosquées en Suisse et dans l'agglomération lausannoise, il est fréquent d'observer des décalages de plusieurs minutes pour l'heure de l'aube (Fajr) ou de la rupture du jeûne (Maghrib).

Pour éviter toute confusion, particulièrement pendant le mois de Ramadan, cet outil automatise la règle islamique de la précaution (الاحتياط). L'objectif est de garantir à la fois la validité absolue du jeûne et celle de la prière, en éliminant le moindre doute.

Le fonctionnement de l'algorithme :
L'outil interroge automatiquement et en temps réel les horaires officiels des principales mosquées de la région, puis applique un filtrage mathématique strict :

**Pour le jeûne (Imsak) : L'algorithme retient l'horaire le plus **tôt** (Minimum) parmi toutes les mosquées. S'arrêter de manger à cette heure garantit à 100% que l'aube légale n'est atteinte nulle part, protégeant ainsi la validité du jeûne.

**Pour l'entrée des prières : L'algorithme retient l'horaire le plus **tardif** (Maximum) pour le Fajr, Dhuhr, Asr, Maghrib et Isha. Prier ou rompre son jeûne (Iftar) à cette heure certifie que le temps légal est définitivement entré, peu importe le calendrier que l'on suit habituellement.

Le fondement juridique :
Cette méthodologie s'appuie sur les recommandations des savants concernant la gestion des divergences de calendriers fiables au sein d'une même ville. L'outil applique littéralement la règle détaillée par la fatwa d'Islamweb.

🔗 Source de référence : Lire la fatwa complète sur Islamweb (n° 418795) - الواجب في الصلاة والصوم عند اختلاف التقاويم : https://www.islamweb.net/ar/fatwa/418795/""")
   
else:

    st.error("Impossible de récupérer les données aujourd'hui.")





