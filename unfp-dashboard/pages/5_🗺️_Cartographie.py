import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import *

# Configuration de la page
st.set_page_config(page_title="Cartographie UNFP", page_icon="🗺️", layout="wide")
st.title("🗺️ Cartographie des Données")

# Chargement des données
df_prefectures = get_prefectures()
df_projects = get_projects()
df_indicators = get_indicators()
df_structures = get_structures()

if df_prefectures.empty:
    st.warning("Aucune donnée géographique disponible.")
    st.stop()

# Menu de sélection de la couche cartographique
st.sidebar.header("Couches Cartographiques")
map_layer = st.sidebar.radio(
    "Sélectionner la couche à afficher:",
    ["Projets", "Indicateurs", "Structures"]
)

# Données pour la carte
if map_layer == "Projets":
    st.header("Répartition Géographique des Projets")
    
    # Compter les projets par préfecture (approximation)
    projects_by_prefecture = run_query("""
        SELECT commune.prefecture_id, COUNT(projet.id) as project_count
        FROM public.projet
        JOIN public.fact_structure structure ON projet.id = structure.id
        JOIN public.dim_commune commune ON structure.commune_id = commune.id
        GROUP BY commune.prefecture_id;
    """)
    
    if projects_by_prefecture[0]:
        project_counts = {pref_id: count for pref_id, count in projects_by_prefecture[0]}
        df_prefectures['project_count'] = df_prefectures['id'].map(project_counts).fillna(0)
        
        # Carte des projets
        fig = px.scatter_mapbox(
            df_prefectures,
            lat="latitude",
            lon="longitude",
            size="project_count",
            color="project_count",
            hover_name="name",
            hover_data={"project_count": True},
            size_max=30,
            zoom=5,
            height=600,
            title="Nombre de projets par préfecture"
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Préfectures couvertes", f"{len(df_prefectures[df_prefectures['project_count'] > 0])}/{len(df_prefectures)}")
        with col2:
            st.metric("Projets totaux", df_prefectures['project_count'].sum())
        with col3:
            st.metric("Moyenne par préfecture", f"{df_prefectures['project_count'].mean():.1f}")

elif map_layer == "Indicateurs":
    st.header("Visualisation des Indicateurs par Préfecture")
    
    # Sélection de l'indicateur
    indicator_options = ["Tous"] + list(df_indicators['indicator_name'].unique())
    selected_indicator = st.sidebar.selectbox("Indicateur", indicator_options)
    
    # Sélection de l'année
    year_options = ["Toutes"] + sorted(list(df_indicators['annee'].unique()), reverse=True)
    selected_year = st.sidebar.selectbox("Année", year_options)
    
    # Filtrer les données
    indicator_data = df_indicators.copy()
    if selected_indicator != "Tous":
        indicator_data = indicator_data[indicator_data['indicator_name'] == selected_indicator]
    if selected_year != "Toutes":
        indicator_data = indicator_data[indicator_data['annee'] == selected_year]
    
    # Préparer les données pour la carte
    map_data = df_prefectures.copy()
    latest_indicators = indicator_data.groupby('prefecture_id')['value'].last().reset_index()

    map_data = map_data.merge(latest_indicators, left_on='id', right_on='prefecture_id', how='left')
    
    # Carte des indicateurs
    if not map_data['value'].isna().all():
        fig = px.scatter_mapbox(
            map_data,
            lat="latitude",
            lon="longitude",
            size="value",
            color="value",
            hover_name="name",
            hover_data={"value": True},
            size_max=40,
            zoom=6,
            height=800,
            title=f"{selected_indicator} par préfecture ({selected_year if selected_year != 'Toutes' else 'Toutes années'})"
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée d'indicateur disponible pour la sélection actuelle.")

elif map_layer == "Structures":
    st.header("Répartition des Structures par Préfecture")
    
    # Compter les structures par préfecture
    structures_by_prefecture = run_query("""
        SELECT commune.prefecture_id, COUNT(fact_structure.id) as structure_count
        FROM public.fact_structure
        JOIN public.dim_commune commune ON fact_structure.commune_id = commune.id
        GROUP BY commune.prefecture_id;
    """)
    
    if structures_by_prefecture[0]:
        structure_counts = {pref_id: count for pref_id, count in structures_by_prefecture[0]}
        df_prefectures['structure_count'] = df_prefectures['id'].map(structure_counts).fillna(0)
        
        # Carte des structures
        fig = px.scatter_mapbox(
            df_prefectures,
            lat="latitude",
            lon="longitude",
            size="structure_count",
            color="structure_count",
            hover_name="name",
            hover_data={"structure_count": True},
            size_max=40,
            zoom=6,
            height=800,
            title="Nombre de structures par préfecture"
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":5,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Préfectures avec structures", f"{len(df_prefectures[df_prefectures['structure_count'] > 0])}/{len(df_prefectures)}")
        with col2:
            st.metric("Structures totales", df_prefectures['structure_count'].sum())
        with col3:
            st.metric("Moyenne par préfecture", f"{df_prefectures['structure_count'].mean():.1f}")

# Tableau des données géographiques
st.subheader("Données Géographiques des Préfectures")
st.dataframe(
    df_prefectures[['name', 'latitude', 'longitude']],
    use_container_width=True,
    height=400
)

# Informations supplémentaires
st.sidebar.info("""
**Note:** Les données de localisation sont basées sur les coordonnées des préfectures.
Pour une visualisation plus précise, des données GPS plus détaillées seraient nécessaires.
""")