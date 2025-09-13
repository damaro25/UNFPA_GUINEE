import streamlit as st
import base64
import os

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord UNFPA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour encoder l'image en base64
def get_base64_of_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Définir les chemins vers les images de fond
BACKGROUND_IMAGE_1 = "./assets/images/unfpa_background.png"
BACKGROUND_IMAGE_2 = "./assets/images/unfpa_fond.png"

# Encoder les images en base64
bg_image_1_base64 = get_base64_of_image(BACKGROUND_IMAGE_1)
bg_image_2_base64 = get_base64_of_image(BACKGROUND_IMAGE_2)

# Utiliser l'image disponible ou une image de secours
if bg_image_1_base64:
    background_image = f"data:image/png;base64,{bg_image_1_base64}"
elif bg_image_2_base64:
    background_image = f"data:image/png;base64,{bg_image_2_base64}"
else:
    # Image de secours depuis une URL si les images locales ne sont pas trouvées
    background_image = "https://raw.githubusercontent.com/streamlit/example-app-background/main/unfpa_guinee_bg.png"

# Style CSS personnalisé avec image de fond
st.markdown(f"""
<style>
    /* Fond de la page principale */
    .stApp {{
        background: url("{background_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}

    /* Overlay pour améliorer la lisibilité */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.88);
        z-index: -1;
    }}

    /* Conteneur principal */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(5px);
    }}

    /* Fond de la sidebar */
    section[data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(135deg, #1f77b4 0%, #2c9fcc 100%);
        background-size: cover;
        background-position: center;
    }}

    .main-header {{
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8);
        font-weight: bold;
    }}

    .metric-card {{
        background-color: rgba(240, 242, 246, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #1f77b4;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
        height: 100%;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }}

    .info-card {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 248, 255, 0.95));
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1f77b4;
        transition: all 0.3s ease;
        height: 100%;
    }}

    .info-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }}

    .stButton button {{
        width: 100%;
        background: linear-gradient(45deg, #1f77b4, #2c9fcc);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-weight: bold;
        transition: all 0.3s ease;
    }}

    .stButton button:hover {{
        background: linear-gradient(45deg, #2c9fcc, #1f77b4);
        transform: scale(1.02);
    }}

    /* Style pour la sidebar */
    .sidebar .sidebar-content {{
        background-color: rgba(255, 255, 255, 0.1) !important;
    }}

    .sidebar-info {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}

    /* Amélioration du texte */
    .stMarkdown {{
        color: #333;
    }}

    /* Responsive design */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: 2rem;
        }}
        .metric-card, .info-card {{
            padding: 1rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# Page d'accueil
st.markdown('<h1 class="main-header">📊 Tableau de Bord UNFPA</h1>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <p style="font-size: 1.2rem; color: #555;">
        Bienvenue dans le tableau de bord de visualisation des données de l'UNFPA.<br>
        Utilisez le menu de navigation sur le côté gauche pour explorer les différentes sections de l'application.
    </p>
</div>
""", unsafe_allow_html=True)

# Métriques principales en page d'accueil
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">📈 Aperçu</h3>
        <p style="color: #555;">Vue d'ensemble des données et indicateurs clés</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">🚀 Projets</h3>
        <p style="color: #555;">Exploration détaillée des projets et leur financement</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">🤝 Partenaires</h3>
        <p style="color: #555;">Analyse des partenaires et de leur contribution</p>
    </div>
    """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">📊 Indicateurs</h3>
        <p style="color: #555;">Suivi des indicateurs de performance par région</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">🗺️ Cartographie</h3>
        <p style="color: #555;">Visualisation géographique des projets et indicateurs</p>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">🔍 Données brutes</h3>
        <p style="color: #555;">Accès aux données brutes pour analyse avancée</p>
    </div>
    """, unsafe_allow_html=True)

# Section supplémentaire pour la cartographie avancée
st.markdown("---")
st.subheader("🌍 Fonctionnalités Avancées")

col7, col8, col9 = st.columns(3)

with col7:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">🌍 Cartographie Avancée</h3>
        <p style="color: #555;">Visualisation géographique avec shapefiles et données spatiales</p>
    </div>
    """, unsafe_allow_html=True)

with col8:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">📱 Rapports Mobiles</h3>
        <p style="color: #555;">Accédez aux données depuis votre appareil mobile</p>
    </div>
    """, unsafe_allow_html=True)

with col9:
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">📤 Export de Données</h3>
        <p style="color: #555;">Exportez les données en CSV, Excel ou PDF</p>
    </div>
    """, unsafe_allow_html=True)

# Ajouter des statistiques globales
st.markdown("---")
st.subheader("📈 Aperçu des Statistiques")

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1f77b4; margin: 0;">Projets Actifs</h3>
        <h2 style="color: #2c9fcc; margin: 10px 0;">42</h2>
    </div>
    """, unsafe_allow_html=True)

with stat_col2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1f77b4; margin: 0;">Budget Total</h3>
        <h2 style="color: #2c9fcc; margin: 10px 0;">12.5M $</h2>
    </div>
    """, unsafe_allow_html=True)

with stat_col3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1f77b4; margin: 0;">Partenaires</h3>
        <h2 style="color: #2c9fcc; margin: 10px 0;">28</h2>
    </div>
    """, unsafe_allow_html=True)

with stat_col4:
    st.markdown("""
    <div class="metric-card">
        <h3 style="color: #1f77b4; margin: 0;">Bénéficiaires</h3>
        <h2 style="color: #2c9fcc; margin: 10px 0;">250K</h2>
    </div>
    """, unsafe_allow_html=True)

# Pied de page dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-info">
    <h4 style="color: #1f77b4; margin-bottom: 10px;">À propos</h4>
    <p style="color: #555; margin-bottom: 5px;">Application de visualisation des données UNFPA.</p>
    <p style="color: #555; margin-bottom: 5px;">Développée avec Streamlit et Plotly.</p>
    <p style="color: #555;">Version 2.0</p>
</div>
""", unsafe_allow_html=True)

# Ajouter un logo UNFPA dans la sidebar (optionnel)
st.sidebar.markdown("---")
try:
    st.sidebar.image("./assets/images/unfpa_logo.png", 
                     use_column_width=True)
except:
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px;">
        <h4 style="color: white;">UNFPA</h4>
        <p style="color: white;">Fonds des Nations Unies pour la population</p>
    </div>
    """, unsafe_allow_html=True)