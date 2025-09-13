import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord UNFP",
    page_icon="📊",
    layout="wide"
)

# Connexion à la base de données
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# Fonctions pour récupérer les données
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def get_domains():
    return run_query("SELECT id, name FROM public.dim_domaine ORDER BY name;")

def get_regions():
    return run_query("SELECT id, name FROM public.dim_region ORDER BY name;")

def get_prefectures():
    return run_query("SELECT id, name FROM public.dim_prefecture ORDER BY name;")

def get_projects():
    return run_query("""
        SELECT p.id, p.nom_projet, p.domaine, p.montant_usd, p.date_debut, p.date_fin, 
               p.bailleur, d.name as domaine_nom
        FROM public.projet p
        LEFT JOIN public.dim_domaine d ON p.domaine = CAST(d.id AS TEXT)
        ORDER BY p.nom_projet;
    """)

def get_partners():
    return run_query("""
        SELECT id, partenaire_name, domaine_id, region_couverte, montant_2025, taux_execution
        FROM public.dim_partenaire
        ORDER BY partenaire_name;
    """)

def get_indicators():
    return run_query("""
        SELECT fi.id, fi.indicator_name, fi.value, fi.annee, dp.name as prefecture_name
        FROM public.fact_indicateur fi
        LEFT JOIN public.dim_prefecture dp ON fi.prefecture_id = dp.id
        ORDER BY fi.indicator_name, fi.annee;
    """)

# Interface utilisateur
st.title("📊 Tableau de Bord UNFP - Visualisation des Données")

# Menu de navigation
menu_options = ["Aperçu", "Projets", "Partenaires", "Indicateurs", "Cartographie"]
selected_tab = st.sidebar.selectbox("Navigation", menu_options)

# Aperçu général
if selected_tab == "Aperçu":
    st.header("Aperçu Général")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_projects = run_query("SELECT COUNT(*) FROM public.projet;")[0][0]
        st.metric("Total des Projets", total_projects)
    
    with col2:
        total_budget = run_query("SELECT SUM(montant_usd) FROM public.projet;")[0][0]
        st.metric("Budget Total (USD)", f"${total_budget:,.2f}")
    
    with col3:
        total_partners = run_query("SELECT COUNT(*) FROM public.dim_partenaire;")[0][0]
        st.metric("Nombre de Partenaires", total_partners)
    
    # Graphique des projets par domaine
    st.subheader("Projets par Domaine")
    projects_by_domain = run_query("""
        SELECT d.name, COUNT(p.id) 
        FROM public.projet p
        LEFT JOIN public.dim_domaine d ON p.domaine = CAST(d.id AS TEXT)
        GROUP BY d.name
        ORDER BY COUNT(p.id) DESC;
    """)
    
    if projects_by_domain:
        df_domain = pd.DataFrame(projects_by_domain, columns=['Domaine', 'Nombre de projets'])
        fig = px.bar(df_domain, x='Domaine', y='Nombre de projets', 
                    title="Répartition des projets par domaine")
        st.plotly_chart(fig, use_container_width=True)
    
    # Budget par bailleur
    st.subheader("Budget par Bailleur")
    budget_by_donor = run_query("""
        SELECT bailleur, SUM(montant_usd) as budget_total
        FROM public.projet
        GROUP BY bailleur
        ORDER BY budget_total DESC;
    """)
    
    if budget_by_donor:
        df_donor = pd.DataFrame(budget_by_donor, columns=['Bailleur', 'Budget Total'])
        fig = px.pie(df_donor, values='Budget Total', names='Bailleur', 
                    title="Répartition du budget par bailleur")
        st.plotly_chart(fig, use_container_width=True)

# Onglet Projets
elif selected_tab == "Projets":
    st.header("Gestion des Projets")
    
    projects = get_projects()
    if projects:
        df_projects = pd.DataFrame(projects, columns=[
            'ID', 'Nom', 'Domaine', 'Budget USD', 'Date début', 'Date fin', 
            'Bailleur', 'Domaine Nom'
        ])
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            domain_filter = st.selectbox(
                "Filtrer par domaine",
                options=["Tous"] + list(df_projects['Domaine Nom'].unique())
            )
        
        with col2:
            donor_filter = st.selectbox(
                "Filtrer par bailleur",
                options=["Tous"] + list(df_projects['Bailleur'].unique())
            )
        
        # Application des filtres
        if domain_filter != "Tous":
            df_projects = df_projects[df_projects['Domaine Nom'] == domain_filter]
        if donor_filter != "Tous":
            df_projects = df_projects[df_projects['Bailleur'] == donor_filter]
        
        # Affichage des données
        st.dataframe(df_projects, use_container_width=True)
        
        # Graphique chronologique
        st.subheader("Évolution des projets dans le temps")
        df_projects['Date début'] = pd.to_datetime(df_projects['Date début'])
        df_timeline = df_projects.groupby(df_projects['Date début'].dt.year).size().reset_index(name='Nombre de projets')
        
        fig = px.line(df_timeline, x='Date début', y='Nombre de projets', 
                     title="Nombre de projets lancés par année")
        st.plotly_chart(fig, use_container_width=True)

# Onglet Partenaires
elif selected_tab == "Partenaires":
    st.header("Partenaires")
    
    partners = get_partners()
    if partners:
        df_partners = pd.DataFrame(partners, columns=[
            'ID', 'Nom', 'Domaine ID', 'Région', 'Montant 2025', 'Taux d\'exécution'
        ])
        
        # Lier avec les noms de domaines
        domains = get_domains()
        domain_dict = {str(id): name for id, name in domains}
        df_partners['Domaine'] = df_partners['Domaine ID'].apply(lambda x: domain_dict.get(str(x), 'Inconnu'))
        
        st.dataframe(df_partners, use_container_width=True)
        
        # Graphique des montants par partenaire
        st.subheader("Engagements financiers des partenaires")
        fig = px.bar(df_partners, x='Nom', y='Montant 2025', 
                    title="Montants engagés par partenaire pour 2025")
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique des taux d'exécution
        st.subheader("Taux d'exécution des partenaires")
        fig = px.scatter(df_partners, x='Nom', y='Taux d\'exécution', 
                        size='Montant 2025', title="Taux d'exécution vs Engagement financier")
        st.plotly_chart(fig, use_container_width=True)

# Onglet Indicateurs
elif selected_tab == "Indicateurs":
    st.header("Indicateurs de Performance")
    
    indicators = get_indicators()
    if indicators:
        df_indicators = pd.DataFrame(indicators, columns=[
            'ID', 'Indicateur', 'Valeur', 'Année', 'Préfecture'
        ])
        
        # Filtres
        indicator_filter = st.selectbox(
            "Sélectionner un indicateur",
            options=list(df_indicators['Indicateur'].unique())
        )
        
        year_filter = st.selectbox(
            "Sélectionner une année",
            options=list(df_indicators['Année'].unique())
        )
        
        # Application des filtres
        filtered_data = df_indicators[
            (df_indicators['Indicateur'] == indicator_filter) & 
            (df_indicators['Année'] == year_filter)
        ]
        
        # Graphique des valeurs par préfecture
        st.subheader(f"Valeurs de {indicator_filter} en {year_filter} par préfecture")
        fig = px.bar(filtered_data, x='Préfecture', y='Valeur', 
                    title=f"{indicator_filter} par préfecture ({year_filter})")
        st.plotly_chart(fig, use_container_width=True)
        
        # Évolution temporelle pour une préfecture sélectionnée
        prefecture_filter = st.selectbox(
            "Sélectionner une préfecture pour voir l'évolution",
            options=list(df_indicators['Préfecture'].unique())
        )
        
        evolution_data = df_indicators[
            (df_indicators['Indicateur'] == indicator_filter) & 
            (df_indicators['Préfecture'] == prefecture_filter)
        ]
        
        if not evolution_data.empty:
            st.subheader(f"Évolution de {indicator_filter} à {prefecture_filter}")
            fig = px.line(evolution_data, x='Année', y='Valeur', 
                         title=f"Évolution de {indicator_filter} à {prefecture_filter}")
            st.plotly_chart(fig, use_container_width=True)

# Onglet Cartographie
elif selected_tab == "Cartographie":
    st.header("Cartographie des Projets et Indicateurs")
    
    # Récupérer les données géographiques
    prefectures_data = run_query("""
        SELECT id, name, latitude, longitude 
        FROM public.dim_prefecture 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
    """)
    
    if prefectures_data:
        df_prefectures = pd.DataFrame(prefectures_data, columns=['ID', 'Nom', 'Latitude', 'Longitude'])
        
        # Compter les projets par préfecture (approximation)
        projects_by_prefecture = run_query("""
            SELECT commune.prefecture_id, COUNT(projet.id)
            FROM public.projet
            JOIN public.fact_structure structure ON projet.id = structure.id
            JOIN public.dim_commune commune ON structure.commune_id = commune.id
            GROUP BY commune.prefecture_id;
        """)
        
        project_counts = {pref_id: count for pref_id, count in projects_by_prefecture}
        df_prefectures['Nombre de projets'] = df_prefectures['ID'].apply(lambda x: project_counts.get(x, 0))
        
        # Carte des projets
        st.subheader("Répartition géographique des projets")
        fig = px.scatter_mapbox(
            df_prefectures,
            lat="Latitude",
            lon="Longitude",
            size="Nombre de projets",
            hover_name="Nom",
            hover_data={"Nombre de projets": True, "Latitude": False, "Longitude": False},
            color="Nombre de projets",
            size_max=30,
            zoom=5,
            height=600
        )
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info(
    "Application de visualisation des données UNFP. "
    "Développée avec Streamlit et Plotly."
)