import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from utils.database import *
import streamlit as st
import tempfile
import os

def load_guinea_shapefile():
    """Charge le shapefile de la Guinée avec les préfectures"""
    try:
        # Chemin vers votre shapefile - à adapter selon votre structure
        shapefile_path = "data/geospatial/gnb_adm2.shp"  # Niveau préfecture
        
        if os.path.exists(shapefile_path):
            gdf = gpd.read_file(shapefile_path)
            # Standardiser les noms pour faire correspondre avec vos données
            gdf['name'] = gdf['admin2Name'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            return gdf
        else:
            st.warning("Shapefile non trouvé. Utilisation des coordonnées des préfectures.")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement du shapefile: {e}")
        return None

def get_projects_with_geodata():
    """Récupère les projets avec données géospatiales"""
    query = """
        SELECT 
            p.id, p.nom_projet, p.domaine, p.montant_usd, p.date_debut, p.date_fin,
            p.bailleur, d.name as domaine_nom,
            c.name as commune_nom, pr.name as prefecture_nom,
            pr.latitude, pr.longitude
        FROM public.projet p
        LEFT JOIN public.dim_domaine d ON p.domaine = CAST(d.id AS TEXT)
        LEFT JOIN public.fact_structure fs ON p.id = fs.id
        LEFT JOIN public.dim_commune c ON fs.commune_id = c.id
        LEFT JOIN public.dim_prefecture pr ON c.prefecture_id = pr.id
        WHERE pr.latitude IS NOT NULL AND pr.longitude IS NOT NULL;
    """
    results, columns = run_query(query)
    return pd.DataFrame(results, columns=columns) if results else pd.DataFrame()

def create_geospatial_dataframe():
    """Crée un GeoDataFrame avec les projets"""
    # Charger les données des projets
    df_projects = get_projects_with_geodata()
    
    if df_projects.empty:
        return None
    
    # Créer un GeoDataFrame à partir des coordonnées
    geometry = gpd.points_from_xy(df_projects.longitude, df_projects.latitude)
    gdf = gpd.GeoDataFrame(df_projects, geometry=geometry, crs="EPSG:4326")
    
    return gdf

def plot_projects_on_map(gdf, metric='count', domain_filter=None):
    """Crée une carte des projets"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Filtrer par domaine si spécifié
    if domain_filter and domain_filter != "Tous":
        gdf = gdf[gdf['domaine_nom'] == domain_filter]
    
    # Agréger les données par préfecture
    if metric == 'count':
        agg_data = gdf.groupby('prefecture_nom').size().reset_index(name='nombre_projets')
        title = 'Nombre de projets par préfecture'
    else:  # budget
        agg_data = gdf.groupby('prefecture_nom')['montant_usd'].sum().reset_index(name='budget_total')
        title = 'Budget total des projets par préfecture'
    
    # Charger le shapefile ou créer une carte basique
    guinea_shapefile = load_guinea_shapefile()
    
    if guinea_shapefile is not None:
        # Fusionner avec le shapefile
        merged = guinea_shapefile.merge(agg_data, left_on='name', right_on='prefecture_nom', how='left')
        merged = merged.to_crs(epsg=3857)  # Pour contextily
        
        # Plot
        if metric == 'count':
            merged.plot(column='nombre_projets', ax=ax, legend=True,
                       cmap='YlOrRd', edgecolor='black', linewidth=0.5)
        else:
            merged.plot(column='budget_total', ax=ax, legend=True,
                       cmap='YlGnBu', edgecolor='black', linewidth=0.5)
        
        # Ajouter le fond de carte
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        
    else:
        # Carte de base avec les points
        gdf.plot(ax=ax, color='red', markersize=50, alpha=0.7)
        
        # Ajouter les noms des préfectures
        for idx, row in gdf.iterrows():
            ax.annotate(row['prefecture_nom'], 
                       (row['longitude'], row['latitude']),
                       xytext=(5, 5), textcoords="offset points",
                       fontsize=8, alpha=0.7)
    
    ax.set_title(title, fontsize=16)
    ax.set_axis_off()
    
    return fig

def create_domain_distribution_map():
    """Carte de distribution des domaines par préfecture"""
    gdf = create_geospatial_dataframe()
    
    if gdf is None or gdf.empty:
        return None
    
    # Compter les projets par domaine et préfecture
    domain_stats = gdf.groupby(['prefecture_nom', 'domaine_nom']).size().reset_index(name='count')
    
    # Pivoter pour avoir les domaines en colonnes
    pivot_df = domain_stats.pivot(index='prefecture_nom', columns='domaine_nom', values='count').fillna(0)
    
    # Normaliser pour avoir des pourcentages
    pivot_df = pivot_df.div(pivot_df.sum(axis=1), axis=0)
    
    return pivot_df

def export_to_shapefile(gdf, output_path):
    """Exporte les données vers un shapefile"""
    try:
        gdf.to_file(output_path, driver='ESRI Shapefile')
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'export: {e}")
        return False