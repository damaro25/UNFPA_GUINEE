import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import *

# Configuration de la page
st.set_page_config(page_title="Partenaires UNFP", page_icon="🤝", layout="wide")
st.title("🤝 Partenaires")

# Chargement des données
df_partners = get_partners()
df_domains = get_domains()

domain_stats = get_domain_stats()

if df_partners.empty:
    st.warning("Aucune donnée de partenaire disponible.")
    st.stop()

# Lier avec les noms de domaines
domain_dict = dict(zip(df_domains['id'], df_domains['name']))
df_partners['domaine_nom'] = df_partners['domaine_id'].map(domain_dict)

# Métriques
col1, col2, col3 = st.columns(3)

with col1:
    total_partners = len(df_partners)
    st.metric("Nombre de partenaires", total_partners)

with col2:
    total_budget = df_partners['montant_2025'].sum()
    st.metric("Engagement total 2025", f"${total_budget:,.2f}")

with col3:
    avg_execution = df_partners['taux_execution'].mean()
    st.metric("Taux d'exécution moyen", f"{avg_execution:.2f}%")

# Filtres
st.sidebar.header("Filtres")

domain_options = ["Tous"] + list(df_domains['name'].unique())
selected_domain = st.sidebar.selectbox("Domaine", domain_options)

# Application des filtres
filtered_partners = df_partners.copy()

if selected_domain != "Tous":
    filtered_partners = filtered_partners[filtered_partners['domaine_nom'] == selected_domain]

# Tableau des partenaires
st.subheader("Liste des Partenaires")
st.dataframe(
    filtered_partners[['partenaire_name', 'domaine_nom', 'region_couverte', 'montant_2025', 'taux_execution']],
    use_container_width=True,
    height=400
)

# Visualisations
col1 = st.columns(1)[0] 

with col1:
    # Engagement par partenaire
    fig = px.bar(filtered_partners, x='partenaire_name', y='montant_2025', 
                title="Engagement financier par partenaire",
                labels={'partenaire_name': 'Partenaire', 'montant_2025': 'Montant 2025 (USD)'})
    st.plotly_chart(fig, use_container_width=True)

col1 = st.columns(1)[0] 
with col1:
    # S'assurer que la colonne est bien numérique
    filtered_partners["montant_2025"] = pd.to_numeric(
        filtered_partners["montant_2025"], errors="coerce"
    )
  
    # Construction du graphique
    fig = px.scatter(
        filtered_partners,
        x="montant_2025",
        y="taux_execution",
        size="montant_2025",
        color="domaine_nom",
        title="Taux d'exécution vs Engagement financier",
        labels={
            "montant_2025": "Engagement (USD)",
            "taux_execution": "Taux d'exécution (%)"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    fig = px.pie(domain_stats, values='nombre_projets', names='domaine_nom', 
                title="Répartition des partenaires par domaine")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(domain_stats, x='domaine_nom', y='budget_total', 
                title="Engagement financier par domaine",
                labels={'domaine_nom': 'Domaine', 'montant_2025': 'Engagement total (USD)'})
    st.plotly_chart(fig, use_container_width=True)

# Détails d'un partenaire sélectionné
st.subheader("Détails du Partenaire")
selected_partner = st.selectbox(
    "Sélectionner un partenaire pour voir les détails",
    options=filtered_partners['partenaire_name'].tolist()
)

if selected_partner:
    partner_details = filtered_partners[filtered_partners['partenaire_name'] == selected_partner].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Nom du partenaire:**", partner_details['partenaire_name'])
        st.write("**Domaine:**", partner_details['domaine_nom'])
        st.write("**Région couverte:**", partner_details['region_couverte'])
    
    with col2:
        st.write("**Engagement 2025:**", f"${partner_details['montant_2025']:,.2f}")
        st.write("**Taux d'exécution:**", f"{partner_details['taux_execution']:.2f}%")
    
    # Projets associés à ce partenaire (approximation basée sur le nom)
    df_projects = get_projects()
    related_projects = df_projects[df_projects['bailleur'].str.contains(selected_partner, case=False, na=False)]
    
    if not related_projects.empty:
        st.subheader("Projets associés")
        st.dataframe(
            related_projects[['nom_projet', 'domaine_nom', 'montant_usd', 'date_debut', 'date_fin']],
            use_container_width=True
        )