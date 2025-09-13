import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import *

# Configuration de la page
st.set_page_config(page_title="Projets UNFP", page_icon="🚀", layout="wide")
st.title("🚀 Gestion des Projets")

# Chargement des données
df_projects = get_projects()
df_domains = get_domains()

if df_projects.empty:
    st.warning("Aucune donnée de projet disponible.")
    st.stop()

# Filtres
st.sidebar.header("Filtres")

domain_options = ["Tous"] + list(df_domains['name'].unique())
selected_domain = st.sidebar.selectbox("Domaine", domain_options)

donor_options = ["Tous"] + list(df_projects['bailleur'].unique())
selected_donor = st.sidebar.selectbox("Bailleur", donor_options)

# Application des filtres
filtered_projects = df_projects.copy()

if selected_domain != "Tous":
    filtered_projects = filtered_projects[filtered_projects['domaine_nom'] == selected_domain]

if selected_donor != "Tous":
    filtered_projects = filtered_projects[filtered_projects['bailleur'] == selected_donor]

# Métriques filtrées
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Projets filtrés", len(filtered_projects))

with col2:
    total_budget = filtered_projects['montant_usd'].sum()
    st.metric("Budget total", f"${total_budget:,.2f}")

with col3:
    avg_budget = filtered_projects['montant_usd'].mean()
    st.metric("Budget moyen", f"${avg_budget:,.2f}")

# Tableau des projets
st.subheader("Liste des Projets")
st.dataframe(
    filtered_projects[['nom_projet', 'domaine_nom', 'bailleur', 'montant_usd', 'date_debut', 'date_fin']],
    use_container_width=True,
    height=400
)

# Visualisations
col1, col2 = st.columns(2)

with col1:
    # Répartition par domaine
    domain_stats = filtered_projects.groupby('domaine_nom').agg({
        'id': 'count',
        'montant_usd': 'sum'
    }).reset_index()
    
    fig = px.pie(domain_stats, values='id', names='domaine_nom', 
                title="Répartition des projets par domaine")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Répartition par bailleur
    donor_stats = filtered_projects.groupby('bailleur').agg({
        'id': 'count',
        'montant_usd': 'sum'
    }).reset_index()
    
    fig = px.bar(donor_stats, x='bailleur', y='montant_usd', 
                title="Budget par bailleur",
                labels={'bailleur': 'Bailleur', 'montant_usd': 'Budget (USD)'})
    st.plotly_chart(fig, use_container_width=True)

# Détails d'un projet sélectionné
st.subheader("Détails du Projet")
selected_project = st.selectbox(
    "Sélectionner un projet pour voir les détails",
    options=filtered_projects['nom_projet'].tolist()
)

if selected_project:
    project_details = filtered_projects[filtered_projects['nom_projet'] == selected_project].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Nom du projet:**", project_details['nom_projet'])
        st.write("**Domaine:**", project_details['domaine_nom'])
        st.write("**Bailleur:**", project_details['bailleur'])
        st.write("**Budget:**", f"${project_details['montant_usd']:,.2f}")
    
    with col2:
        st.write("**Date de début:**", project_details['date_debut'])
        st.write("**Date de fin:**", project_details['date_fin'])
        st.write("**Intitulé:**", project_details['intitule'])
    
    # Résultats attendus et atteints
    if project_details['resultats_attendus'] or project_details['resultats_atteints']:
        st.subheader("Résultats")
        
        if project_details['resultats_attendus']:
            st.write("**Résultats attendus:**")
            st.info(project_details['resultats_attendus'])
        
        if project_details['resultats_atteints']:
            st.write("**Résultats atteints:**")
            st.success(project_details['resultats_atteints'])