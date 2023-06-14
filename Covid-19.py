import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, Fullscreen
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static

# Set up the Streamlit app
st.set_page_config(page_title="COVID-19 Top 10", page_icon=":microbe:", layout="wide")

# Define the base URL for the COVID-19 API
base_url = "https://corona.lmao.ninja/v2/countries"

# Get the data from the API
response = requests.get(base_url)
if response.status_code == 200:
    try:
        data = response.json()
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response from API")
        st.stop()
else:
    st.error("Failed to retrieve data from API")
    st.stop()

# Create a pandas DataFrame from the data
df = pd.DataFrame(data)

# Sort the DataFrame by the number of confirmed cases
df = df.sort_values(by=["cases"], ascending=False)

# Select only the top 10 countries
df_top10 = df.head(10)

# Create a folium map centered on the world
m = folium.Map(location=[30, 0], zoom_start=2)

# Define a dictionary of tile layer options
tile_options = {
    "OpenStreetMap": folium.TileLayer(),
    "Stamen Terrain": folium.TileLayer(
        tiles="https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png",
        attr="Stamen",
        name="Stamen Terrain",
        overlay=True,
        control=False
    ),
    "Stamen Watercolor": folium.TileLayer(
        tiles="https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png",
        attr="Stamen",
        name="Stamen Watercolor",
        overlay=True,
        control=False
    )
}

# Add a dropdown menu to choose the tile layer
tile_layer = st.sidebar.selectbox(
    "Select tile layer",
    list(tile_options.keys())
)

# Add the selected tile layer to the map
tile_options[tile_layer].add_to(m)

# Add a marker cluster layer to the map
marker_cluster = MarkerCluster().add_to(m)

# Define a function to add a marker to the map for each row in the DataFrame
def add_marker(row):
    location = [row["countryInfo"]["lat"], row["countryInfo"]["long"]]
    flag_url = row["countryInfo"]["flag"]
    tooltip = f"""
    <div style="background-color: #F5F5F5; border-radius: 5px; padding: 5px;">
        <img src="{flag_url}" style="height:30px;width:auto;margin-right:5px;">{row['country']}<br>
        Confirmed cases: {row['cases']}<br>
        Active cases: {row['active']}<br>
        Recovered: {row['recovered']}<br>
        Deaths: {row['deaths']}<br>
    </div>
    """
    icon = folium.features.CustomIcon(flag_url, icon_size=(30, 30))
    folium.Marker(location=location, tooltip=tooltip, icon=icon).add_to(marker_cluster)

# Add a marker to the map for each row in the DataFrame
df_top10.apply(add_marker, axis=1)
# Create a plotly bar chart
fig = px.bar(df_top10, x="country", y="cases", color="country",
             labels={"cases": "Confirmed Cases"}, title="Top 10 Countries by Confirmed COVID-19 Cases")

# Define the sidebar
st.sidebar.title("COVID-19 Top 10 Dashboard")
st.sidebar.markdown("Welcome to the COVID-19 Top 10 Dashboard! This dashboard displays the top 10 countries by confirmed COVID-19 cases.")

# Add a funky background image
st.markdown(
    """
    <style>
    body {
        background-image: url('https://i.imgur.com/78G7Itx.png');
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add the plotly chart to the Streamlit app
st.plotly_chart(fig, use_container_width=True)
# Sort the DataFrame by the number of recovered cases
df = df.sort_values(by=["recovered"], ascending=False)

# Select only the top 10 countries
df_top10 = df.head(10)

# Create a plotly pie chart
fig_pie = px.pie(df_top10, values='recovered', names='country',
                 title='Top 10 Countries by Recovered COVID-19 Cases')

# Customize the pie chart
fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                      marker=dict(colors=px.colors.qualitative.Pastel))


# Add the plotly chart to the Streamlit app
st.plotly_chart(fig_pie, use_container_width=True)
# Display the map in Streamlit
st.markdown("## Top 10 Countries by Confirmed COVID-19 Cases")
folium_static(m, width=900, height=600)
