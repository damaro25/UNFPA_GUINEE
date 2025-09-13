import psycopg2
import pandas as pd
import streamlit as st
from functools import lru_cache

@st.cache_resource
def init_connection():
    """Initialise la connexion à la base de données"""
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"]
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

@st.cache_data(ttl=600)
def run_query(query, params=None):
    """Exécute une requête SQL et retourne les résultats"""
    conn = init_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return results, columns
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return None, []
    finally:
        if conn:
            #conn.close()
            pass

def get_domains():
    """Récupère la liste des domaines"""
    results, columns = run_query("SELECT id, name FROM public.dim_domaine ORDER BY name;")
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_regions():
    """Récupère la liste des régions"""
    results, columns = run_query("SELECT id, name FROM public.dim_region ORDER BY name;")
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_prefectures():
    """Récupère la liste des préfectures"""
    results, columns = run_query("""
        SELECT id, name, latitude, longitude 
        FROM public.dim_prefecture 
        ORDER BY name;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_communes():
    """Récupère la liste des communes"""
    results, columns = run_query("""
        SELECT c.id, c.name, p.name as prefecture_name
        FROM public.dim_commune c
        LEFT JOIN public.dim_prefecture p ON c.prefecture_id = p.id
        ORDER BY c.name;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_projects():
    """Récupère la liste des projets"""
    results, columns = run_query("""
        SELECT p.id, p.nom_projet, p.intitule, p.intitule_en_abrege, p.domaine_id, p.montant_usd, 
               p.date_debut, p.date_fin, p.bailleur, 
               p.resultats_attendus, p.resultats_atteints,
               d.name as domaine_nom
        FROM public.dim_projet p
        LEFT JOIN public.dim_domaine d ON p.domaine_id = d.id
        ORDER BY p.nom_projet;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_partners():
    """Récupère la liste des partenaires"""
    results, columns = run_query("""
        SELECT id, partenaire_name, domaine_id, region_couverte, 
               montant_2025, taux_execution
        FROM public.dim_partenaire
        ORDER BY partenaire_name;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_indicators():
    """Récupère les indicateurs"""
    results, columns = run_query("""
        SELECT fi.id, fi.indicator_name, fi.value, fi.annee, 
               dp.name as prefecture_name, dp.id as prefecture_id
        FROM public.fact_indicateur fi
        JOIN public.dim_prefecture dp ON fi.prefecture_id = dp.id
        ORDER BY  fi.value DESC;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_planning():
    """Récupère les données de planning"""
    results, columns = run_query("""
        SELECT id, annee, cible, realise
        FROM public.fact_planning
        ORDER BY annee;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()

def get_structures():
    """Récupère les structures"""
    results, columns = run_query("""
        SELECT fs.id, fs.domaine_id, fs.commune_id, fs.org_name,
               d.name as domaine_nom, c.name as commune_name
        FROM public.fact_structure fs
        LEFT JOIN public.dim_domaine d ON fs.domaine_id = d.id
        LEFT JOIN public.dim_commune c ON fs.commune_id = c.id
        ORDER BY fs.org_name;
    """)
    if results:
        return pd.DataFrame(results, columns=columns)
    return pd.DataFrame()


def get_domain_stats():
    """Calcule les statistiques détaillées par domaine"""
    query = """
        SELECT 
            d.id,
            d.name as domaine_nom,
            p.nom_projet as projet_name,
            p.intitule_en_abrege as projet_name_abrege,
            COUNT(p.id) as nombre_projets,
            SUM(p.montant_usd) as budget_total,
            AVG(p.montant_usd) as budget_moyen,
            MIN(p.date_debut) as premier_projet,
            MAX(p.date_debut) as dernier_projet,
            COUNT(DISTINCT p.bailleur) as nombre_bailleurs,
            COUNT(DISTINCT pt.id) as nombre_partenaires,
            COUNT(DISTINCT fs.id) as nombre_structures
        FROM public.dim_domaine d
        LEFT JOIN public.dim_projet p ON p.domaine_id = d.id
        LEFT JOIN public.dim_partenaire pt ON pt.domaine_id = d.id
        LEFT JOIN public.fact_structure fs ON fs.domaine_id = d.id
        GROUP BY d.id, d.name, p.nom_projet, p.intitule_en_abrege
        ORDER BY budget_total DESC;
    """
    results, columns = run_query(query)
    return pd.DataFrame(results, columns=columns) if results else pd.DataFrame()



