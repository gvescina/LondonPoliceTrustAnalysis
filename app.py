from flask import Flask, render_template, request, jsonify, url_for
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('data/filtered_stop_and_search.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.dropna(subset=['Latitude', 'Longitude'])
df = df[df['Latitude'].apply(lambda x: isinstance(x, (float, int))) &
        df['Longitude'].apply(lambda x: isinstance(x, (float, int)))]

# Define icon paths based on crime types
icon_paths = {
    "Evidence of offences under the Act": "evidence.png",
    "Stolen goods": "stolen_goods.png",
    "Controlled drugs": "controlled_drugs.png",
    "Offensive weapons": "offensive_weapons.png",
    "Articles for use in criminal damage": "criminal_damage.png",
    "Firearms": "firearms.png",
    "Anything to threaten or harm anyone": "threaten_harm.png",
    "Fireworks": "fireworks.png",
}


def create_map(filtered_df):
    # Adjust the initial zoom and center as needed
    m = folium.Map(location=[51.479865, -0.118092], zoom_start=11, tiles='OpenStreetMap')

    marker_cluster = MarkerCluster().add_to(m)
    for idx, row in filtered_df.iterrows():
        crime_type = row['Object of search']
        icon_path = icon_paths.get(crime_type, "default.png")
        icon_file_path = os.path.join(app.root_path, 'static/icons', icon_path)
        icon = folium.CustomIcon(icon_file_path, icon_size=(30, 30))  # Resize to 30x30 pixels

        popup_content = (
            f"<b>Date:</b> {row['Date'].strftime('%Y-%m-%d')}<br>"
            f"<b>Borough:</b> {row['Borough']}<br>"
            f"<b>Ethnicity:</b> {row['Officer-defined ethnicity']}<br>"
            f"<b>Object of search:</b> {row['Object of search']}<br>"
            f"<b>Outcome:</b> {row['Outcome']}"
        )

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content),
            icon=icon
        ).add_to(marker_cluster)

    return m._repr_html_()


@app.route('/')
def index():
    # Remove NaN values
    ethnicities = df['Officer-defined ethnicity'].dropna().unique()
    crime_types = df['Object of search'].dropna().unique()
    outcomes = df['Outcome'].unique()

    map_html = create_map(df)
    return render_template('index.html', ethnicities=ethnicities, crime_types=crime_types, outcomes=outcomes,
                           min_date=df['Date'].min().date(), max_date=df['Date'].max().date(), map_html=map_html)


@app.route('/filter', methods=['POST'])
def filter_data():
    filters = request.json
    start_date = pd.to_datetime(filters['start_date'])
    end_date = pd.to_datetime(filters['end_date'])
    ethnicity = filters['ethnicity']
    crime_type = filters['crime_type']
    outcome = filters['outcome']

    filtered_df = df[
        (df['Date'] >= start_date) & (df['Date'] <= end_date) &
        ((df['Officer-defined ethnicity'] == ethnicity) if ethnicity != 'All' else True) &
        ((df['Object of search'] == crime_type) if crime_type != 'All' else True) &
        ((df['Outcome'] == outcome) if outcome != 'All' else True)
        ]

    map_html = create_map(filtered_df)
    return map_html


if __name__ == '__main__':
    app.run(debug=True, port=5002)
