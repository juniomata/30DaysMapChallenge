import requests 
import pandas as pd
import geopandas as gpd
import json
import folium
import matplotlib.colors as mcolors
from mapclassify import NaturalBreaks

# Define the ArcGIS REST API query URL for GeoJSON format 
query_url = "https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/28/query"
params = {
    "where": "1=1",  # Select all features
    "outFields": "*",  # Get all fields
    "f": "geojson"  # Request GeoJSON format
}

# Make a request to the server
response = requests.get(query_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    geojson_data = response.json()

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    print("Data Fetching Success")
else:
    print("Error fetching data:", response.status_code)

# Custom color mapping
custom_color_map = {
    "Geothermal": "#d53e4f",
    "Solar": "#fdae61",
    "Wind": "#fee08b",
    "Biomass": "#e6f598",
    "Pumped Storage": "#24ce98",
    "Hydroelectric": "#1e90ff",
    "Tidal": "#5e4FA2",
    "Other": "grey"
}
default_color = "grey"

# Define bin edges and size scale using Natural Breaks classification
nb = NaturalBreaks(gdf["Renew_MW"], k=5)
gdf["size_class"] = pd.cut(gdf["Renew_MW"], bins=nb.bins, labels=[3, 7, 10, 15], include_lowest=True)

# Create the folium map
m = folium.Map(location=[39.833333, -98.583333], zoom_start=5, tiles="CartoDB dark_matter")

# Add title
title_html = '<h3 style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index:99999; background-color: rgba(255, 255, 255, 0.7); padding: 10px; border-radius: 5px;">North America Renewable Energy Plants</h3>'
m.get_root().html.add_child(folium.Element(title_html))

# Add points to the map
for _, row in gdf.iterrows():
    folium.CircleMarker(
        location=(row["Latitude"], row["Longitude"]),
        radius=row["size_class"],
        color=custom_color_map.get(row["PrimRenew"], default_color),
        weight=0.5,
        fill=True,
        fill_color=custom_color_map.get(row["PrimRenew"], default_color),
        fill_opacity=0.55,
        popup=folium.Popup(f"Facility: {row['Facility']}<br>Capacity: {row['Renew_MW']} MW<br>Energy Source: {row['PrimRenew']}<br>Owner: {row['Owner']}<br>City: {row['City']}<br>State/Province: {row['StateProv']}", max_width=450)
    ).add_to(m)

# Add collapsible legend
legend_html = """
<button id='show-legend-btn' style='position: fixed; bottom: 20px; left: 20px; background-color: white; border: 2px solid grey; padding: 10px 15px; border-radius: 5px; font-weight: bold; cursor: pointer; z-index: 99999; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);' onclick="document.getElementById('legend-box').style.display='block'; this.style.display='none';">Show Legend</button>
<div id='legend-box' style='display: none; position: fixed; bottom: 50px; left: 20px; width: 300px; height: auto; 
background-color: white; z-index:99999; font-size:14px; padding: 10px; border:2px solid grey; border-radius: 5px;'>
    <b>Sources</b> 
    <button onclick="document.getElementById('legend-box').style.display='none'; document.getElementById('show-legend-btn').style.display='block';">Hide</button><br>
"""
for source, color in custom_color_map.items():
    legend_html += f'<i style="background:{color}; width: 20px; height: 20px; float: left; margin-right: 10px;"></i> {source}<br>'
legend_html += "<br><b>Capacity (MW)</b><br>"
for i, value in enumerate(nb.bins[1:]):
    legend_html += f'<i style="display:inline-block; width:{[3, 7, 10, 15][i]*2.25}px; height:{[3, 7, 10, 15][i]*2.25}px; background:grey; border-radius:50%;"></i> < {value:.1f} MW<br>'
legend_html += "<br><br><i>Data Source: <a href='https://esricanada.maps.arcgis.com/home/item.html?id=96102cac5134489a8c69aa81931d8604' target='_blank'>Esri Canada</a></i>"
legend_html += "</div>"

m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
map_filename = "renewableplants.html"
m.save(map_filename)

m