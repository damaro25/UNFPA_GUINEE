import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import *

# Configuration de la page
st.set_page_config(page_title="Indicateurs UNFP", page_icon="📈", layout="wide")
st.title("📈 Indicateurs de Performance")

# Chargement des données
df_indicators = get_indicators()
df_prefectures = get_prefectures()

if df_indicators.empty:
    st.warning("Aucune donnée d'indicateur disponible.")
    st.stop()

# Filtres
st.sidebar.header("Filtres")

indicator_options = ["Tous"] + list(df_indicators['indicator_name'].unique())
selected_indicator = st.sidebar.selectbox("Indicateur", indicator_options)

year_options = ["Toutes"] + sorted(list(df_indicators['annee'].unique()), reverse=True)
selected_year = st.sidebar.selectbox("Année", year_options)

prefecture_options = ["Toutes"] + list(df_indicators['prefecture_name'].unique())
selected_prefecture = st.sidebar.selectbox("Préfecture", prefecture_options)

# Application des filtres
filtered_indicators = df_indicators.copy()

if selected_indicator != "Tous":
    filtered_indicators = filtered_indicators[filtered_indicators['indicator_name'] == selected_indicator]

if selected_year != "Toutes":
    filtered_indicators = filtered_indicators[filtered_indicators['annee'] == selected_year]

if selected_prefecture != "Toutes":
    filtered_indicators = filtered_indicators[filtered_indicators['prefecture_name'] == selected_prefecture]

# Métriques
st.subheader("Aperçu des Indicateurs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    unique_indicators = filtered_indicators['indicator_name'].nunique()
    st.metric("Indicateurs uniques", unique_indicators)

with col2:
    unique_years = filtered_indicators['annee'].nunique()
    st.metric("Années couvertes", unique_years)

with col3:
    unique_prefectures = filtered_indicators['prefecture_name'].nunique()
    st.metric("Préfectures couvertes", unique_prefectures)

with col4:
    total_records = len(filtered_indicators)
    st.metric("Enregistrements", total_records)

# Visualisations
if selected_indicator == "Tous" and selected_year == "Toutes":
    # Vue d'ensemble de tous les indicateurs
    st.subheader("Vue d'ensemble de tous les indicateurs")
    
    indicator_stats = df_indicators.groupby('indicator_name').agg({
        'value': 'count',
        'prefecture_name': 'nunique',
        'annee': 'nunique'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(indicator_stats, x='indicator_name', y='value', 
                    title="Nombre de mesures par indicateur",
                    labels={'indicator_name': 'Indicateur', 'value': 'Nombre de mesures'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(indicator_stats, x='value', y='prefecture_name',
                        size='annee', color='indicator_name',
                        title="Couverture des indicateurs",
                        labels={'value': 'Mesures', 'prefecture_name': 'Préfectures couvertes'})
        st.plotly_chart(fig, use_container_width=True)

else:
    # Analyse détaillée d'un indicateur spécifique
    if selected_indicator != "Tous":
        st.subheader(f"Analyse de l'indicateur: {selected_indicator}")
        
        # Données pour l'indicateur sélectionné
        indicator_data = df_indicators[df_indicators['indicator_name'] == selected_indicator]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution temporelle
            yearly_avg = indicator_data.groupby('annee')['value'].mean().reset_index()
            fig = px.line(yearly_avg, x='annee', y='value',
                         title=f"Évolution de {selected_indicator}",
                         labels={'annee': 'Année', 'value': 'Valeur moyenne'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribution par préfecture (pour la dernière année)
            latest_year = indicator_data['annee'].max()
            latest_data = indicator_data[indicator_data['annee'] == latest_year]
            
            if not latest_data.empty:
                fig = px.bar(latest_data, x='prefecture_name', y='value',
                            title=f"{selected_indicator} par préfecture ({latest_year})",
                            labels={'prefecture_name': 'Préfecture', 'value': 'Valeur'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Carte choroplèthe (si des données géographiques sont disponibles)
        st.subheader("Visualisation Géographique")
        
        # Préparer les données pour la carte
        map_data = indicator_data.copy()
        map_data = map_data.merge(df_prefectures[['id', 'latitude', 'longitude']], 
                                 left_on='prefecture_id', right_on='id', how='left')
        
        # Pour la dernière année disponible
        latest_map_data = map_data[map_data['annee'] == latest_year]
        
        if not latest_map_data.empty and latest_map_data['latitude'].notna().any():
            fig = px.scatter_mapbox(
                latest_map_data,
                lat="latitude",
                lon="longitude",
                size="value",
                color="value",
                hover_name="prefecture_name",
                hover_data={"value": True, "annee": True},
                size_max=30,
                zoom=5,
                height=500,
                title=f"{selected_indicator} par préfecture ({latest_year})"
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données géographiques insuffisantes pour afficher la carte.")

# Tableau des données
st.subheader("Données des Indicateurs")
st.dataframe(
    filtered_indicators[['indicator_name', 'value', 'annee', 'prefecture_name']],
    use_container_width=True,
    height=400
)

# Téléchargement des données
csv = filtered_indicators.to_csv(index=False)
st.download_button(
    label="Télécharger les données en CSV",
    data=csv,
    file_name="indicateurs_unfp.csv",
    mime="text/csv"
)