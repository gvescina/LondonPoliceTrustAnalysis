from flask import Flask, render_template, request, jsonify
import pandas as pd
import folium
from folium.plugins import MarkerCluster

app = Flask(__name__)

df = pd.read_csv('data/filtered_stop_and_search.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.dropna(subset=['Latitude', 'Longitude'])
df = df[df['Latitude'].apply(lambda x: isinstance(x, (float, int))) &
        df['Longitude'].apply(lambda x: isinstance(x, (float, int)))]


df = df.dropna(subset=['Officer-defined ethnicity', 'Object of search'])

def create_map(filtered_df):
    m = folium.Map(location=[51.43, -0.1278], zoom_start=11, tiles='OpenStreetMap')

    marker_cluster = MarkerCluster().add_to(m)
    for idx, row in filtered_df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(f"Borough: {row['Borough']}<br>Ethnicity: {row['Officer-defined ethnicity']}<br>Object of search: {row['Object of search']}<br>Outcome: {row['Outcome']}"),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    return m._repr_html_()

@app.route('/')
def index():
    ethnicities = df['Officer-defined ethnicity'].unique()
    crime_types = df['Object of search'].unique()
    outcomes = df['Outcome'].unique()
    map_html = create_map(df)
    return render_template('index.html', ethnicities=ethnicities, crime_types=crime_types, outcomes=outcomes, min_date=df['Date'].min().date(), max_date=df['Date'].max().date(), map_html=map_html)

@app.route('/filter', methods=['POST'])
def filter_data():
    filters = request.json
    start_date = pd.to_datetime(filters['start_date'])
    end_date = pd.to_datetime(filters['end_date'])
    ethnicity = filters['ethnicity']
    crime_type = filters['crime_type']
    outcome = filters['outcome']

    # Apply filters to the dataframe
    filtered_df = df[
        (df['Date'] >= start_date) & (df['Date'] <= end_date) &
        ((df['Officer-defined ethnicity'] == ethnicity) if ethnicity != 'All' else True) &
        ((df['Object of search'] == crime_type) if crime_type != 'All' else True) &
        ((df['Outcome'] == outcome) if outcome != 'All' else True)
    ]

    # Generate the updated map
    map_html = create_map(filtered_df)
    return map_html

if __name__ == '__main__':
    app.run(debug=True)
