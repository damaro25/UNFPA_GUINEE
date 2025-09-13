import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Mobilisation des Ressources - UNFPA",
    page_icon="💰",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .resource-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .progress-bar {
        height: 20px;
        background-color: #e9ecef;
        border-radius: 10px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background-color: #1f77b4;
        border-radius: 10px;
        text-align: center;
        color: white;
        line-height: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Titre de la page
st.markdown('<h1 class="main-header">💰 Mobilisation des Ressources - UNFPA Guinée</h1>', unsafe_allow_html=True)

# Introduction
st.markdown("""
Cette plateforme présente un tableau de bord complet de la mobilisation des ressources pour les programmes et projets du UNFPA en Guinée.
Visualisez les engagements financiers, les écarts de financement et les performances des partenaires.
""")

# Données de démonstration (à remplacer par vos vraies données)
@st.cache_data
def load_resource_data():
    # Données des bailleurs de fonds
    donors_data = {
        'Bailleur': ['UE', 'USAID', 'Banque Mondiale', 'Gouvernement Guinéen', 'Canada', 'Suède', 'Japon', 'UNICEF', 'OMS', 'Fonds Mondial'],
        'Engagement_2024': [2500000, 1800000, 2200000, 1500000, 950000, 850000, 750000, 600000, 550000, 500000],
        'Deboursement_2024': [1950000, 1500000, 1800000, 1200000, 800000, 700000, 600000, 500000, 450000, 400000],
        'Type': ['International', 'International', 'International', 'National', 'International', 'International', 'International', 'UN', 'UN', 'International']
    }
    
    # Données des projets par domaine
    projects_data = {
        'Domaine': ['Santé reproductive', 'Égalité des genres', 'Population et développement', 'Jeunesse', 'Urgences'],
        'Budget_total': [3500000, 2200000, 1800000, 1200000, 900000],
        'Finance_acquise': [2800000, 1800000, 1500000, 900000, 600000],
        'Pourcentage_finance': [80, 82, 83, 75, 67]
    }
    
    # Données temporelles
    dates = pd.date_range(start='2023-01-01', end='2024-06-01', freq='M')
    time_data = {
        'Mois': dates,
        'Engagements': np.random.randint(200000, 500000, len(dates)).cumsum(),
        'Deboursements': np.random.randint(150000, 450000, len(dates)).cumsum()
    }
    
    return pd.DataFrame(donors_data), pd.DataFrame(projects_data), pd.DataFrame(time_data)

# Chargement des données
donors_df, projects_df, time_df = load_resource_data()

# Métriques clés
st.subheader("📊 Indicateurs Clés de Mobilisation des Ressources")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_budget = projects_df['Budget_total'].sum()
    st.metric("Budget Total", f"{total_budget:,.0f} USD")
    
with col2:
    total_funding = projects_df['Finance_acquise'].sum()
    st.metric("Financement Acquise", f"{total_funding:,.0f} USD")
    
with col3:
    funding_gap = total_budget - total_funding
    st.metric("Déficit de Financement", f"{funding_gap:,.0f} USD")
    
with col4:
    funding_rate = (total_funding / total_budget) * 100
    st.metric("Taux de Financement", f"{funding_rate:.1f}%")

# Barre de progression du financement
st.markdown("**Progression du financement global**")
progress_html = f"""
<div class="progress-bar">
    <div class="progress-fill" style="width: {funding_rate}%">{funding_rate:.1f}%</div>
</div>
"""
st.markdown(progress_html, unsafe_allow_html=True)

# Onglets pour différentes vues
tab1, tab2, tab3, tab4 = st.tabs(["Bailleurs de Fonds", "Projets par Domaine", "Évolution Temporelle", "Analyse des Gaps"])

with tab1:
    st.subheader("🤝 Bailleurs de Fonds et Partenaires")
    
    # Graphique des engagements par bailleur
    fig = px.bar(donors_df, x='Bailleur', y='Engagement_2024', 
                 color='Type', title="Engagements des Bailleurs en 2024 (USD)",
                 labels={'Engagement_2024': 'Montant Engagé (USD)', 'Bailleur': 'Bailleur de Fonds'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Taux de décaissement par bailleur
    donors_df['Taux_Deboursement'] = (donors_df['Deboursement_2024'] / donors_df['Engagement_2024']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(donors_df, x='Bailleur', y='Taux_Deboursement', 
                     title="Taux de Déboursement par Bailleur (%)",
                     labels={'Taux_Deboursement': 'Taux de Déboursement (%)', 'Bailleur': 'Bailleur de Fonds'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(donors_df, values='Engagement_2024', names='Bailleur', 
                     title="Répartition des Engagements par Bailleur")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé des bailleurs
    st.subheader("Tableau Détaillé des Bailleurs")
    donors_display = donors_df.copy()
    donors_display['Engagement_2024'] = donors_display['Engagement_2024'].apply(lambda x: f"{x:,.0f} USD")
    donors_display['Deboursement_2024'] = donors_display['Deboursement_2024'].apply(lambda x: f"{x:,.0f} USD")
    donors_display['Taux_Deboursement'] = donors_display['Taux_Deboursement'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(donors_display, use_container_width=True)

with tab2:
    st.subheader("📋 Financement par Domaine d'Intervention")
    
    # Graphique des budgets par domaine
    fig = px.bar(projects_df, x='Domaine', y='Budget_total', 
                 title="Budget Total par Domaine (USD)",
                 labels={'Budget_total': 'Budget Total (USD)', 'Domaine': 'Domaine d Intervention'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Diagramme en entonnoir du financement
    fig = px.funnel(projects_df, x='Budget_total', y='Domaine', 
                    title='Budget Total par Domaine',
                    labels={'Budget_total': 'Budget Total (USD)', 'Domaine': 'Domaine d Intervention'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Financement acquis vs budget
    projects_melted = projects_df.melt(id_vars=['Domaine'], 
                                      value_vars=['Budget_total', 'Finance_acquise'],
                                      var_name='Type', value_name='Montant')
    
    fig = px.bar(projects_melted, x='Domaine', y='Montant', color='Type',
                 barmode='group', title='Budget vs Financement Acquis par Domaine',
                 labels={'Montant': 'Montant (USD)', 'Domaine': 'Domaine d Intervention'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des projets
    st.subheader("Détail du Financement par Domaine")
    projects_display = projects_df.copy()
    projects_display['Budget_total'] = projects_display['Budget_total'].apply(lambda x: f"{x:,.0f} USD")
    projects_display['Finance_acquise'] = projects_display['Finance_acquise'].apply(lambda x: f"{x:,.0f} USD")
    projects_display['Pourcentage_finance'] = projects_display['Pourcentage_finance'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(projects_display, use_container_width=True)

with tab3:
    st.subheader("📈 Évolution Temporelle des Ressources")
    
    # Graphique d'évolution des engagements et décaissements
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_df['Mois'], y=time_df['Engagements'], 
                             mode='lines+markers', name='Engagements', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=time_df['Mois'], y=time_df['Deboursements'], 
                             mode='lines+markers', name='Décaissements', line=dict(color='green')))
    
    fig.update_layout(title='Évolution des Engagements et Décaissements au fil du temps',
                      xaxis_title='Mois',
                      yaxis_title='Montant (USD)',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Graphique à barres empilées mensuelles
    time_df['Mois_str'] = time_df['Mois'].dt.strftime('%Y-%m')
    time_df['Engagements_Mensuels'] = time_df['Engagements'].diff().fillna(time_df['Engagements'])
    time_df['Deboursements_Mensuels'] = time_df['Deboursements'].diff().fillna(time_df['Deboursements'])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=time_df['Mois_str'], y=time_df['Engagements_Mensuels'], 
                         name='Engagements Mensuels', marker_color='blue'))
    fig.add_trace(go.Bar(x=time_df['Mois_str'], y=time_df['Deboursements_Mensuels'], 
                         name='Décaissements Mensuels', marker_color='green'))
    
    fig.update_layout(title='Engagements et Décaissements Mensuels',
                      xaxis_title='Mois',
                      yaxis_title='Montant (USD)',
                      barmode='group')
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("🔍 Analyse des Gaps de Financement")
    
    # Calcul des gaps par domaine
    projects_df['Gap'] = projects_df['Budget_total'] - projects_df['Finance_acquise']
    
    # Graphique des gaps de financement
    fig = px.bar(projects_df, x='Domaine', y='Gap', 
                 title="Gap de Financement par Domaine (USD)",
                 labels={'Gap': 'Déficit de Financement (USD)', 'Domaine': 'Domaine d Intervention'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Carte thermique des priorités de financement
    projects_df['Priorite'] = projects_df['Gap'] / projects_df['Budget_total'] * 100
    fig = px.imshow([projects_df['Priorite'].values], 
                    labels=dict(x="Domaines", y="Priorité", color="Niveau de Priorité"),
                    x=projects_df['Domaine'].values,
                    color_continuous_scale='Reds',
                    title="Priorité de Financement par Domaine")
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("Recommandations Stratégiques")
    
    for idx, row in projects_df.iterrows():
        with st.expander(f"Recommandations pour {row['Domaine']} (Déficit: {row['Gap']:,.0f} USD)"):
            st.markdown(f"""
            **Niveau de priorité:** {'Élevé' if row['Priorite'] > 30 else 'Moyen' if row['Priorite'] > 15 else 'Faible'}
            
            **Stratégies proposées:**
            - Identifier de nouveaux bailleurs spécialisés dans le domaine
            - Renforcer les partenariats existants
            - Développer des propositions de projet ciblées
            - Explorer les financements innovants (privé, fondations)
            
            **Objectif:** Réduire le gap de {row['Gap']:,.0f} USD
            """)

# Section de projections et objectifs
st.markdown("---")
st.subheader("🎯 Projections et Objectifs 2024-2025")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Objectifs de Mobilisation 2024-2025:**
    - Atteindre 90% de financement pour tous les domaines
    - Élargir la base de bailleurs de 25%
    - Réduire le délai moyen de décaissement à 45 jours
    - Diversifier les sources de financement
    """)

with col2:
    # Graphique des objectifs
    objectives_data = {
        'Objectif': ['Taux de financement', 'Nouveaux bailleurs', 'Délai de décaissement', 'Diversification'],
        'Valeur_actuelle': [funding_rate, 15, 60, 65],
        'Valeur_cible': [90, 25, 45, 85]
    }
    objectives_df = pd.DataFrame(objectives_data)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Valeur Actuelle', x=objectives_df['Objectif'], y=objectives_df['Valeur_actuelle']))
    fig.add_trace(go.Bar(name='Valeur Cible', x=objectives_df['Objectif'], y=objectives_df['Valeur_cible']))
    
    fig.update_layout(barmode='group', title='Objectifs de Performance 2024-2025',
                      yaxis_title='Valeur (%) / Jours')
    st.plotly_chart(fig, use_container_width=True)

# Section de téléchargement et export
st.markdown("---")
st.subheader("📤 Export des Données")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Exporter données bailleurs"):
        csv = donors_df.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name="unfpa_bailleurs_ressources.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📋 Exporter données projets"):
        csv = projects_df.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name="unfpa_projets_financement.csv",
            mime="text/csv"
        )

with col3:
    if st.button("📈 Exporter données temporelles"):
        csv = time_df.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name="unfpa_evolution_ressources.csv",
            mime="text/csv"
        )

# Pied de page
st.markdown("---")
st.caption("Dernière mise à jour: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
st.caption("UNFPA Guinée - Plateforme de Mobilisation des Ressources")