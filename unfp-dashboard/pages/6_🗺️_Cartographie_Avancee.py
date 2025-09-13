import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import tempfile
import os
from utils.database import get_projects


# === Données simulées ===
df_stats = pd.DataFrame({
    "N_PREFECTU": ["CONAKRY", "KINDIA", "BOFFA", "DUBREKA", "MACENTA"],
    "budget_total": [1_000_000, 2_500_000, 1_200_000, 900_000, 3_300_000],
    "nombre_projets": [8, 15, 5, 3, 8]
})

# === Chargement et traitement du shapefile ===
gdf = gpd.read_file("data/shapefiles/GN_LIMITE_PREFECTURES.shp").to_crs(epsg=4326)
gdf["N_PREFECTU"] = gdf["N_PREFECTU"].str.upper()
gdf = gdf.merge(df_stats, on="N_PREFECTU", how="left")
gdf["lon"] = gdf.geometry.centroid.x
gdf["lat"] = gdf.geometry.centroid.y

gdf = gpd.read_file("C:/Users/Laby Damaro CAMARA/UNFPA_GUINEE/unfp-dashboard/data/shapefiles/GN_LIMITE_PREFECTURES.shp")




# === Génération de la carte interactive ===
def generer_carte(z_col):
    gdf_merged = gdf.merge(df, left_on='N_REGION', right_on='region')
    total = gdf_merged[z_col].sum()
    pourcentages = gdf_merged[z_col] / total * 100
    hovertexts = [
        f"<b>{row.N_PREFECTU}</b><br>{z_col.replace('_', ' ').title()}: {row._asdict()[z_col]:,.0f}" +
        f"<br>Part nationale: {pct:.1f}%"
        for row, pct in zip(gdf_merged.itertuples(), pourcentages)
    ]

    fig = go.Figure(go.Choroplethmapbox(
        geojson=gdf_merged.__geo_interface__,
        locations=gdf_merged.index,
        z=gdf_merged[z_col].fillna(0),
        colorscale="YlGnBu" if z_col == "nombre_projets" else "YlOrRd",
        marker_opacity=0.8,
        marker_line_width=0.2,
        colorbar_title="Projets" if z_col == "nombre_projets" else "USD",
        hovertext=hovertexts,
        hoverinfo="text"
    ))

    fig.add_trace(go.Scattermapbox(
        lat=gdf_merged["latitude"],
        lon=gdf_merged["longitude"],
        text=gdf_merged["N_PREFECTU"],
        mode="text",
        textfont=dict(size=10, color="black"),
        showlegend=False
    ))

    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_zoom=6,
        mapbox_center={"lat": gdf_merged["latitude"].mean(), "lon": gdf_merged["longitude"].mean()},
        margin=dict(l=10, r=10, t=30, b=10),
        height=550,
        title=f"{'Répartition du Budget Total (USD)' if z_col == 'budget_total' else 'Répartition du Nombre de Projets'} par Préfecture",
        title_font_size=16,
        title_x=0.5
    )
    return fig





# Configuration de la page
st.set_page_config(
    page_title="Carte des Projets UNFP",
    page_icon="🗺️",
    layout="wide"
)

# Titre de l'application
st.title("🗺️ Carte des Projets UNFP par Région")
st.markdown("Visualisation géographique du nombre de projets par région et préfecture")

# Fonction pour charger les données (à adapter selon votre source de données)
@st.cache_data
def load_data():
    # Données simulées - à remplacer par vos vraies données
    data = {
        'region': ['Conakry'.upper(), 'Kindia'.upper(), 'Mamou'.upper(), 'Labe'.upper(), 'Kankan'.upper(), 'Faranah'.upper(), 'Boke'.upper(), "N'zerekore".upper()],
        'nombre_projets': [45, 32, 28, 25, 22, 18, 15, 12],
        'latitude': [9.6412, 10.0556, 10.3755, 11.3167, 10.3845, 10.0404, 10.9322, 7.7548],
        'longitude': [-13.5784, -12.8658, -12.0913, -12.2833, -9.3056, -10.7434, -14.2906, -8.8179]
    }
    return pd.DataFrame(data)

# Charger les données
df = load_data()

# Sidebar pour les filtres
st.sidebar.header("Filtres")
st.sidebar.info("Utilisez ces filtres pour affiner la visualisation")

# Option pour choisir le type de visualisation
vis_type = st.sidebar.radio(
    "Type de visualisation",
    ["Carte Choroplèthe", "Carte à Points", "Graphique à Barres"]
)

# Section principale
tab1, tab2, tab3 = st.tabs(["Carte", "Données", "Statistiques"])

with tab1:
    if vis_type == "Carte Choroplèthe":

        # Texte descriptif
        st.caption("Cette carte met en lumière la répartition géographique des projets UNFPA en Guinée, en mettant en évidence les zones les plus actives en termes de fonds alloués et des projets déployés à l'échelle nationale.")

        projets = get_projects()
        # Dropdown pour sélectionner la métrique
        metrique = st.selectbox(
            "Sélectionnez le projet à visualiser:",
            options=projets.intitule_en_abrege.unique().tolist(),
            index=0,
            key="metrique-carte"
        )
        metric_column = "nombre_projets" if metrique == "Appui à la participation des femmes à la transition" else "budget_total"
                

        #st.header("Répartition Géographique")
        
        # Fusionner avec vos données
        gdf_merged = gdf.merge(df, left_on='N_REGION', right_on='region')



        fig = generer_carte("nombre_projets")
        
      
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif vis_type == "Carte à Points":
        st.subheader("Carte à Points des Projets par Région")
        
        # Créer une carte à points avec Plotly
        fig = px.scatter_geo(
            df,
            lat='latitude',
            lon='longitude',
            size='nombre_projets',
            color='nombre_projets',
            hover_name='region',
            hover_data={'nombre_projets': True, 'latitude': False, 'longitude': False},
            size_max=30,
            color_continuous_scale="Viridis",
            title="Nombre de projets par région"
        )
        
        fig.update_geos(
            resolution=50,
            showcoastlines=True,
            coastlinecolor="RebeccaPurple",
            showland=True,
            landcolor="LightGreen",
            showocean=True,
            oceancolor="LightBlue",
            showlakes=True,
            lakecolor="Blue",
            showrivers=True,
            rivercolor="Blue"
        )
        
        fig.update_layout(height=600, margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.subheader("Graphique à Barres des Projets par Région")
        
        # Trier les données par nombre de projets
        df_sorted = df.sort_values('nombre_projets', ascending=True)
        
        # Créer un graphique à barres horizontales
        fig = px.bar(
            df_sorted,
            x='nombre_projets',
            y='region',
            orientation='h',
            color='nombre_projets',
            color_continuous_scale="Blues",
            labels={'nombre_projets': 'Nombre de projets', 'region': 'Région'},
            title="Nombre de projets par région"
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Données des Projets par Région")
    
    # Afficher les données sous forme de tableau
    st.dataframe(
        df,
        column_config={
            "region": "Région",
            "nombre_projets": "Nombre de projets",
            "latitude": "Latitude",
            "longitude": "Longitude"
        },
        use_container_width=True
    )
    
    # Options d'exportation
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name="projets_par_region.csv",
            mime="text/csv"
        )
    
    with col2:
        # Pour Excel, on utiliserait df.to_excel() avec un buffer
        st.info("Export Excel disponible sur demande")

with tab3:
    st.subheader("Statistiques des Projets")
    
    # Calculer quelques statistiques
    total_projets = df['nombre_projets'].sum()
    moyenne_projets = df['nombre_projets'].mean()
    max_projets = df['nombre_projets'].max()
    region_max = df.loc[df['nombre_projets'].idxmax(), 'region']
    
    # Afficher les métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total des projets", f"{total_projets}")
    
    with col2:
        st.metric("Moyenne par région", f"{moyenne_projets:.1f}")
    
    with col3:
        st.metric("Maximum", f"{max_projets}")
    
    with col4:
        st.metric("Région la plus active", region_max)
    
    # Répartition en pourcentage
    st.subheader("Répartition des Projets (%)")
    df['pourcentage'] = (df['nombre_projets'] / total_projets) * 100
    
    fig = px.pie(
        df,
        values='pourcentage',
        names='region',
        title="Répartition en pourcentage des projets par région"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Section d'information
st.sidebar.markdown("---")
st.sidebar.info("""
**À propos de cette visualisation:**
- Les données sont basées sur les projets de l'UNFP
- Les régions sont celles de la Guinée
- Les nombres de projets sont illustratifs
""")

# Instructions pour utiliser un vrai shapefile
with st.expander("ℹ️ Instructions pour utiliser un vrai Shapefile"):
    st.markdown("""
    ### Pour utiliser un vrai Shapefile de la Guinée:
    
    1. Téléchargez un Shapefile des régions de la Guinée
    2. Placez les fichiers (.shp, .shx, .dbf) dans un dossier accessible
    3. Utilisez le code suivant pour charger le Shapefile:
    
    ```python
    import geopandas as gpd
    
    # Charger le shapefile
    gdf = gpd.read_file("chemin/vers/votre/shapefile.shp")
    
    # Fusionner avec vos données
    gdf_merged = gdf.merge(df, left_on='nom_region', right_on='region')
    
    # Créer la carte
    fig = px.choropleth(
        gdf_merged,
        geojson=gdf_merged.geometry,
        locations=gdf_merged.index,
        color='nombre_projets',
        hover_name='nom_region',
        color_continuous_scale="Blues"
    )
    ```
    """)

# Pied de page
st.markdown("---")
st.caption("Application de visualisation des projets UNFP - Données illustratives")