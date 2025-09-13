import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.database import *
import base64




# Définir les chemins vers les images de fond
BACKGROUND_IMAGE_1 = "assets/images/unfpa_background.png"
BACKGROUND_IMAGE_2 = "assets/images/unfpa_fond.png"

# Configuration de la page
st.set_page_config(page_title="Aperçu UNFP", page_icon="📊", layout="wide")

# Fonction pour ajouter une image de fond
def add_bg_from_local(image_file=BACKGROUND_IMAGE_2):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Fond de la sidebar */
        section[data-testid="stSidebar"] > div:first-child {{
            background: url("{BACKGROUND_IMAGE_2}");
            background-size: cover;
            background-position: center;
        }}

        
        /* Ajouter un overlay pour améliorer la lisibilité */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Style pour les métriques */
        .metric-card {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #1f77b4;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        /* Style pour les graphiques */
        .plotly-graph-div {{
            background-color: rgba(255, 255, 255, 0.85) !important;
            border-radius: 10px;
            padding: 10px;
        }}
        
        /* Style pour les titres */
        h1, h2, h3, h4, h5, h6 {{
            color: #1f77b4 !important;
            text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Ajouter l'image de fond (remplacez par le chemin de votre image)
# Vous pouvez télécharger une image et la placer dans le même répertoire
try:
    add_bg_from_local(BACKGROUND_IMAGE_2)
except:
    # Fallback si l'image n'est pas trouvée
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .main .block-container {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-card {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #1f77b4;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("📊 Aperçu Général")

# Métriques clés
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_projects = run_query("SELECT COUNT(*) FROM public.projet;")[0][0]
    st.markdown(f'<div class="metric-card"><h3>Total des Projets</h3><h2>{total_projects[0]}</h2></div>', unsafe_allow_html=True)

with col2:
    total_budget = run_query("SELECT SUM(montant_usd) FROM public.projet;")[0][0]
    budget_value = f"{total_budget[0]:.2f}" if total_budget[0] else "0"
    st.markdown(f'<div class="metric-card"><h3>Budget Total</h3><h2>{budget_value} USD</h2></div>', unsafe_allow_html=True)

with col3:
    total_partners = run_query("SELECT COUNT(*) FROM public.dim_partenaire;")[0][0]
    st.markdown(f'<div class="metric-card"><h3>Partenaires</h3><h2>{total_partners[0]:.0f}</h2></div>', unsafe_allow_html=True)

with col4:
    total_structures = run_query("SELECT COUNT(*) FROM public.fact_structure;")[0][0]
    st.markdown(f'<div class="metric-card"><h3>Structures</h3><h2>{total_structures[0]}</h2></div>', unsafe_allow_html=True)

# Graphiques principaux
col1, col2 = st.columns(2)

with col1:
    # Projets par domaine
    st.subheader("Projets par Domaine")
    projects_by_domain = run_query("""
        SELECT d.name, COUNT(p.id) as count
        FROM public.projet p
        LEFT JOIN public.dim_domaine d ON p.domaine = CAST(d.id AS TEXT)
        GROUP BY d.name
        ORDER BY count DESC;
    """)
    
    if projects_by_domain[0]:
        df_domain = pd.DataFrame(projects_by_domain[0], columns=projects_by_domain[1])
        fig = px.bar(df_domain, x='name', y='count', 
                    title="Répartition des projets par domaine",
                    labels={'name': 'Domaine', 'count': 'Nombre de projets'})
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Budget par bailleur
    st.subheader("Budget par Bailleur")
    budget_by_donor = run_query("""
        SELECT bailleur, SUM(montant_usd) as budget_total
        FROM public.projet
        GROUP BY bailleur
        ORDER BY budget_total DESC;
    """)
    
    if budget_by_donor[0]:
        df_donor = pd.DataFrame(budget_by_donor[0], columns=budget_by_donor[1])
        fig = px.pie(df_donor, values='budget_total', names='bailleur', 
                    title="Répartition du budget par bailleur")
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)

# Évolution temporelle
st.subheader("Évolution des Projets dans le Temps")
timeline_data = run_query("""
    SELECT EXTRACT(YEAR FROM date_debut) as year, COUNT(*) as count, SUM(montant_usd) as budget
    FROM public.projet
    WHERE date_debut IS NOT NULL
    GROUP BY EXTRACT(YEAR FROM date_debut)
    ORDER BY year;
""")

if timeline_data[0]:
    df_timeline = pd.DataFrame(timeline_data[0], columns=timeline_data[1])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_timeline['year'], y=df_timeline['count'], 
                            name="Nombre de projets", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_timeline['year'], y=df_timeline['budget']/1000000, 
                            name="Budget (millions USD)", yaxis="y2", line=dict(color='red')))
    
    fig.update_layout(
        title="Évolution du nombre de projets et du budget",
        xaxis_title="Année",
        yaxis_title="Nombre de projets",
        yaxis2=dict(title="Budget (millions USD)", overlaying="y", side="right"),
        legend=dict(x=0, y=1.1, orientation="h"),
        plot_bgcolor='rgba(255, 255, 255, 0.8)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Indicateurs de performance
st.subheader("Indicateurs de Performance")
planning_data = get_planning()

if not planning_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(planning_data, x='annee', y=['cible', 'realise'], 
                     title="Évolution des cibles et réalisations",
                     labels={'value': 'Valeur', 'variable': 'Type', 'annee': 'Année'})
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        planning_data['taux'] = planning_data['realise'] / planning_data['cible'] * 100
        fig = px.bar(planning_data, x='annee', y='taux', 
                    title="Taux de réalisation (%)",
                    labels={'taux': 'Taux de réalisation (%)', 'annee': 'Année'})
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)

# Ajouter cette section après les métriques principales
st.subheader("📊 Analyse par Domaine")

domain_stats = get_domain_stats()

if not domain_stats.empty:
    # KPI par domaine
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        top_domain = domain_stats.iloc[0]['domaine_nom']
        st.markdown(f'<div class="metric-card"><h3>Domaine le plus financé</h3><h2>{top_domain}</h2></div>', unsafe_allow_html=True)
    
    with col2:
        total_budget = domain_stats['budget_total'].sum()
        st.markdown(f'<div class="metric-card"><h3>Budget total</h3><h2>${total_budget:,.2f}</h2></div>', unsafe_allow_html=True)
    
    with col3:
        avg_budget = domain_stats['budget_total'].mean()
        st.markdown(f'<div class="metric-card"><h3>Budget moyen</h3><h2>${avg_budget:,.2f}</h2></div>', unsafe_allow_html=True)
    
    with col4:
        total_projects = domain_stats['nombre_projets'].sum()
        st.markdown(f'<div class="metric-card"><h3>Total projets</h3><h2>{total_projects}</h2></div>', unsafe_allow_html=True)

    # Graphiques comparatifs
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(domain_stats, x='domaine_nom', y='budget_total',
                    title="Budget total par domaine",
                    labels={'domaine_nom': 'Domaine', 'budget_total': 'Budget (USD)'})
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(domain_stats, values='budget_total', names='domaine_nom',
                    title="Répartition du budget par domaine")
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)

    # Analyse détaillée
    st.subheader("📋 Détails par Domaine")
    
    # Tableau interactif
    st.dataframe(
        domain_stats[[
            'domaine_nom', 'nombre_projets', 'budget_total', 
            'budget_moyen', 'nombre_bailleurs', 'nombre_partenaires'
        ]],
        use_container_width=True,
        height=400
    )

    # Cartographie de l'efficacité
    st.subheader("📈 Efficacité des Domaines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Assurer que la colonne est bien numérique
        domain_stats["budget_moyen"] = (
            pd.to_numeric(domain_stats["budget_moyen"], errors="coerce")
        )

        # Remplacer les None/NaN par 0 (ou une autre valeur par défaut)
        domain_stats["budget_moyen"] = domain_stats["budget_moyen"].fillna(0)

        # Ensuite tracer
        fig = px.scatter(
            domain_stats,
            x="nombre_projets",
            y="budget_moyen",
            size="budget_moyen",
            color="domaine_nom",
            title="Budget vs Nombre de projets",
            labels={"nombre_projets": "Nombre de projets", "budget_total": "Budget total"}
        )
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Nombre de partenaires par domaine
        fig = px.bar(domain_stats, x='domaine_nom', y='nombre_partenaires',
                    title="Partenaires par domaine",
                    labels={'domaine_nom': 'Domaine', 'nombre_partenaires': 'Nombre de partenaires'})
        fig.update_layout(plot_bgcolor='rgba(255, 255, 255, 0.8)')
        st.plotly_chart(fig, use_container_width=True)