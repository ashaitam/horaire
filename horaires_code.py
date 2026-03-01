import streamlit as st
import requests
import re
from datetime import datetime, timedelta
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
        "mosques": ["Association Al-Taqwa", "CCML", "Mosquée Omar Ibn Al Khattab- Crissier", "Centre d'études islamiques Boukhari", "Centre Assalam", "Fondation Al Hikma"],
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
        "mosques": [
            "Mosquée An-Nour (Melun)", 
            "Mosquée ACDFT DITIB (Melun)", 
            "Mosquée AMCV (Cesson)",
            "Mosquée Alsalam (Dammarie-Les-Lys)",
            "Mosquée UMM (Le Mée-sur-Seine)",
            "Mosquée Ibn Badis (Le Mée-sur-Seine)"
        ],
        "urls": [
            "https://mawaqit.net/fr/annour-melun",
            "https://mawaqit.net/fr/acdft-melun-ditib-melun-77000-france",
            "https://mawaqit.net/fr/amcv-cesson-vsd",
            "https://mawaqit.net/fr/mosquee-alsalam-de-dammarie-les-lys-dammarie-les-lys-77190-france",
            "https://mawaqit.net/fr/umm-mee",
            "https://mawaqit.net/fr/mosquee-abdelhamid-ibn-badis-le-mee-sur-seine-77350-france"
        ]
    }
}

# --- MENU DÉROULANT CENTRAL ---
options_menu = ["-- Sélectionnez une ville --"] + list(villes_data.keys())
ville_choisie = st.selectbox("📍 Choisissez votre ville :", options_menu)

st.divider()

# --- BLOCAGE DE L'AFFICHAGE ---
if ville_choisie == "-- Sélectionnez une ville --":
    st.info("👆 Veuillez choisir une ville dans le menu ci-dessus pour afficher les horaires de prière correspondants.")

else:
    mosques = villes_data[ville_choisie]["mosques"]
    urls = villes_data[ville_choisie]["urls"]

    st.markdown(f"""
    - **{ville_choisie}**
    - L'horaire est mis à jour chaque jour à minuit""")
    
    fajr_compare, duhr_compare, asr_compare, maghrib_compare, icha_compare = [], [], [], [], []

    # --- EXTRACTION DES DONNÉES ---
    total_mosques = len(urls)
    mosques_success = 0  
    
    with st.spinner("Récupération des horaires en cours..."):
        for url in urls:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    match = re.search(r'"times":\[(.*?)\]', response.text)
                    if match:
                        mosques_success += 1  
                        
                        horaires_bruts = match.group(1).replace('"', '').split(',')
                        if len(horaires_bruts) == 6:
                            fajr_compare.append(horaires_bruts[0])
                            duhr_compare.append(horaires_bruts[2])
                            asr_compare.append(horaires_bruts[3])
                            maghrib_compare.append(horaires_bruts[4])
                            icha_compare.append(horaires_bruts[5])
                        elif len(horaires_bruts) == 5:
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

        # --- CALCUL DU PROCHAIN ÉVÉNEMENT ---
        def temps_restant(heure_cible_str, est_demain=False):
            h, m = map(int, heure_cible_str.split(':'))
            cible = maintenant.replace(hour=h, minute=m, second=0, microsecond=0)
            
            if est_demain:
                cible += timedelta(days=1)
                
            diff = cible - maintenant
            heures = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return heures, minutes

        if heure_str < imsak:
            prochain_nom = "🛑 Imsak"
            h_rest, m_rest = temps_restant(imsak)
        elif heure_str < fajr:
            prochain_nom = "🌅 Fajr"
            h_rest, m_rest = temps_restant(fajr)
        elif heure_str < duhr:
            prochain_nom = "☀️ Dhuhr"
            h_rest, m_rest = temps_restant(duhr)
        elif heure_str < asr:
            prochain_nom = "🌤️ Asr"
            h_rest, m_rest = temps_restant(asr)
        elif heure_str < maghrib:
            prochain_nom = "🍲 Maghrib"
            h_rest, m_rest = temps_restant(maghrib)
        elif heure_str < icha:
            prochain_nom = "🌙 Isha"
            h_rest, m_rest = temps_restant(icha)
        else:
            prochain_nom = "🔄 Mise à jour des horaires"
            h_rest, m_rest = temps_restant("00:00", est_demain=True)

        if h_rest > 0:
            temps_texte = f"**{h_rest}h et {m_rest} min**"
        else:
            temps_texte = f"**{m_rest} minutes**"

        # --- AFFICHAGE DE L'INTERFACE ---
        st.success(f"⏳ **Prochain événement :** {prochain_nom} dans {temps_texte}.")
        
       
        st.write("") 
        
        st.error(f"🛑 **IMSAK (Arrêt de la nourriture) : {imsak}**")
        st.info(f"🌅 **FAJR (Heure de prière) : {fajr}**")
        
        st.write("") 
        
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
st.caption(f"✅ **Santé des données :** {mosques_success}/{total_mosques} mosquées scannées avec succès.")
st.progress(mosques_success / total_mosques)
st.divider()        
st.info("""
**À propos** : Cet outil automatisé a été développé par **Haitam SHAIM**, utilisation à but lucratif interdite.

**Support & Contact** : En cas de bug, de problème d'affichage ou pour toute question, n'hésitez pas à me [contacter ici](mailto:haitam.shaim@gmail.com).
""")

st.caption("Développé par **Haitam SHAIM**, 2026.")





