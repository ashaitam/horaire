import streamlit as st
import requests
import re
from datetime import datetime
from zoneinfo import ZoneInfo

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Horaires de Prière", page_icon="🕌", layout="centered")

st.warning("⚠️ **Version Bêta** : Cette application est actuellement en phase de test. Veuillez ne pas vous baser exclusivement sur ces résultats pour le moment et vérifier auprès de votre mosquée.")

tz_suisse = ZoneInfo("Europe/Zurich")
maintenant = datetime.now(tz_suisse)
date_str = maintenant.strftime("%d.%m.%Y")
heure_str = maintenant.strftime("%H:%M")

st.caption(f"📅 **Aujourd'hui :** {date_str} &nbsp;&nbsp;|&nbsp;&nbsp; ⏰ **Heure locale :** {heure_str}")

# --- TITRE ET EN-TÊTE ---
st.title("🕌 Horaires de Prière")

# --- DONNÉES ET LISTES ---
villes_data = {
    "Lausanne": {
        "mosques": ["Association Al-Taqwa", "CCML", "Mosquée Omar Crissier", "Boukhari", "Assalam", "Al Hikma"],
        "urls": [
            "https://mawaqit.net/fr/association-al-taqwa-lausanne-1018-switzerland-1",
            "https://mawaqit.net/fr/ccml",
            "https://mawaqit.net/fr/omar-crissier",
            "https://mawaqit.net/fr/alboukhari-lausanne",
            "https://mawaqit.net/fr/assala-lausanne",
            "https://mawaqit.net/fr/alhikma-lausanne"
        ]
    },
    "Région Cesson-Melun": {
        "mosques": ["Mosquée An-Nour (FCMM)", "Mosquée ACDFT DITIB"],
        "urls": [
            "https://mawaqit.net/fr/annour-melun",
            "https://mawaqit.net/fr/acdft-melun-ditib-melun-77000-france"
        ]
    }
}

# --- MENU DÉROULANT CENTRAL (AVEC CHOIX PAR DÉFAUT VIDE) ---
# On crée une liste d'options qui commence par un texte d'attente
options_menu = ["-- Sélectionnez une ville --"] + list(villes_data.keys())

ville_choisie = st.selectbox("📍 Choisissez votre ville :", options_menu)

st.divider()

# --- BLOCAGE DE L'AFFICHAGE TANT QUE LA VILLE N'EST PAS CHOISIE ---
if ville_choisie == "-- Sélectionnez une ville --":
    # Message d'accueil quand aucune ville n'est sélectionnée
    st.info("👆 Veuillez choisir une ville dans le menu ci-dessus pour afficher les horaires de précaution correspondants.")

else:
    # TOUT CE QUI EST EN DESSOUS NE S'AFFICHE QUE SI UNE VRAIE VILLE EST CHOISIE
    
    mosques = villes_data[ville_choisie]["mosques"]
    urls = villes_data[ville_choisie]["urls"]

    st.markdown(f"""
    - **{ville_choisie}**
    - L'horaire est mis à jour chaque jour à minuit""")
    
    fajr_compare, duhr_compare, asr_compare, maghrib_compare, icha_compare = [], [], [], [], []

    # --- EXTRACTION DES DONNÉES ---
    with st.spinner("Récupération des horaires en cours..."):
        for url in urls:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    match = re.search(r'"times":\[(.*?)\]', response.text)
                    if match:
                        horaires_bruts = match.group(1).replace('"', '').split(',')
                        fajr_compare.append(horaires_bruts[0])
                        duhr_compare.append(horaires_bruts[1])
                        asr_compare.append(horaires_bruts[2])
                        maghrib_compare.append(horaires_bruts[3])
                        icha_compare.append(horaires_bruts[4])
            except Exception:
                continue
                
        if ville_choisie == "Lausanne" and len(icha_compare) > 1:
            icha_compare.pop(1)

    # --- CALCULS DE PRÉCAUTION ---
    if fajr_compare: 
        imsak = min(fajr_compare)
        fajr = max(fajr_compare)
        duhr = max(duhr_compare)
        asr = max(asr_compare)
        maghrib = max(maghrib_compare)
        icha = max(icha_compare)

        # --- AFFICHAGE DE L'INTERFACE ---
        st.error(f"🛑 **IMSAK (Arrêt de la nourriture) : {imsak}**")
        st.info(f"🌅 **FAJR (Heure de prière) : {fajr}**")
        
        st.write("") # Petit espace visuel
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(label="☀️ Dhuhr", value=duhr)
        with col2: st.metric(label="🌤️ Asr", value=asr)
        with col3: st.metric(label="🍲 Maghrib", value=maghrib)
        with col4: st.metric(label="🌙 Isha", value=icha)
            
        st.divider()

        # --- DÉTAILS TRANSPARENTS ---
        with st.expander(f"Voir les mosquées scannées ({ville_choisie})"):
            for m in mosques:
                st.write(f"- {m}")
                
        with st.expander("Source des données"):
            st.markdown("""**Ce n'est en aucun cas nous qui fixons ou calculons ces horaires.** Ils sont strictement définis et mis à jour par les mosquées elles-mêmes.  
            Notre outil se contente de récupérer leurs horaires officiels (via le système Mawaqit) et d'effectuer une simple comparaison mathématique pour trouver le plus tôt et le plus tard.""")
            
        with st.expander("Comment ça marche ?"):
            st.markdown("""
Face à la diversité des méthodes de calcul (degrés d'inclinaison du soleil) utilisées par les différentes mosquées en Suisse et dans l'agglomération lausannoise, il est fréquent d'observer des décalages de plusieurs minutes pour l'heure de l'aube (Fajr) ou de la rupture du jeûne (Maghrib).

Pour éviter toute confusion, particulièrement pendant le mois de Ramadan, cet outil automatise la règle de la précaution (الاحتياط). L'objectif est de garantir à la fois la validité absolue du jeûne et celle de la prière, en éliminant le moindre doute.

**Le fonctionnement de l'algorithme :**
L'outil interroge automatiquement et en temps réel les horaires officiels des principales mosquées de la région, puis applique un filtrage mathématique strict :

* **Pour le jeûne (Imsak) :** L'algorithme retient l'horaire le plus **tôt** (Minimum) parmi toutes les mosquées. S'arrêter de manger à cette heure garantit à 100% que l'aube légale n'est atteinte nulle part, protégeant ainsi la validité du jeûne.
* **Pour l'entrée des prières :** L'algorithme retient l'horaire le plus **tardif** (Maximum) pour le Fajr, Dhuhr, Asr, Maghrib et Isha. Prier ou rompre son jeûne (Iftar) à cette heure certifie que le temps légal est définitivement entré, peu importe le calendrier que l'on suit habituellement.

**Le fondement juridique :**
Cette méthodologie s'appuie sur les recommandations des savants concernant la gestion des divergences de calendriers fiables au sein d'une même ville. L'outil applique littéralement la règle détaillée par la fatwa d'Islamweb.

🔗 **Source de référence :** [Lire la fatwa complète sur Islamweb (n° 418795)](https://www.islamweb.net/ar/fatwa/418795/)
            """)
    else:
        st.error("Impossible de récupérer les données aujourd'hui.")

# --- PIED DE PAGE ---
st.divider()

st.info("""
**À propos** : Cet outil automatisé a été développé par **Haitam SHAIM**, utilisation à but lucratif interdite.

**Support & Contact** : En cas de bug, de problème d'affichage ou pour toute question, n'hésitez pas à me [contacter ici](mailto:haitam.shaim@gmail.com).
""")

st.caption("Développé par **Haitam SHAIM**, 2026.")
