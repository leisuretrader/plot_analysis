
import requests
from io import StringIO
import pandas as pd
import random
import plotly.graph_objects as go
import plotly.subplots as sp

def download_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return StringIO(response.text)
    else:
        return None

def switch_coordinates(coord_str):
    coords = coord_str.split(', ')
    return float(coords[1]), float(coords[0])

def get_airport_codes(csv_url):
    csv_file = download_csv(csv_url)
    airport_codes = pd.read_csv(csv_file)[['iata_code', 'coordinates']].dropna().reset_index(drop=True)
    airport_codes[['latitude', 'longitude']] = airport_codes['coordinates'].apply(switch_coordinates).apply(pd.Series)
    airport_codes['dummy_values'] = airport_codes.apply(lambda row: random.randint(1000, 20000), axis=1)
    return airport_codes

def merge_dataframes(airport_codes, new_data, on_key='iata_code'):
    merged_data = airport_codes.merge(new_data, on=on_key, how='left')
    return merged_data

def find_missing_keys(airport_codes, new_data, key='iata_code'):
    missing_keys = set(new_data[key]) - set(airport_codes[key])
    return missing_keys

def airport_locator(airport_codes, iata_code):
    return airport_codes.loc[airport_codes['iata_code'] == iata_code.upper()]

def plot_airport_map(airport_codes):
    # Calculate the threshold for the top 10% values
    top_10_percent_threshold = airport_codes['dummy_values'].quantile(0.9)

    # Split the data into top 10% and the rest
    top_10_percent_data = airport_codes[airport_codes['dummy_values'] >= top_10_percent_threshold]
    rest_data = airport_codes[airport_codes['dummy_values'] < top_10_percent_threshold]

    fig = go.Figure()

    # Create a subplot with 1 row and 2 columns
    # fig = sp.make_subplots(
    #     rows=1, cols=2,
    #     column_widths=[0.4, 0.6],
    #     specs=[[{"type": "table"}, {"type": "scattergeo"}]],
    #     horizontal_spacing=0.05
    # )
    # # Add a table trace for the airport_codes DataFrame
    # fig.add_trace(go.Table(
    #     header=dict(
    #         values=['IATA Code', 'Latitude', 'Longitude', 'Dummy Values'],
    #         font=dict(size=12),
    #         align='left'
    #     ),
    #     cells=dict(
    #         values=[airport_codes['iata_code'], airport_codes['latitude'], airport_codes['longitude'], airport_codes['dummy_values']],
    #         align='left'
    #     ),
    #     columnwidth=[1, 1, 1, 1]
    # ), row=1, col=1)

    # Add a trace for the rest of the data
    fig.add_trace(go.Scattergeo(
        lat=rest_data['latitude'],
        lon=rest_data['longitude'],
        text=rest_data.apply(lambda row: f"{row['iata_code']}", axis=1),
        hoverinfo='text',
        mode='markers+text',
        textposition='bottom center',
        textfont=dict(color='darkblue'),
        marker=dict(
            size=rest_data['dummy_values'] / 1000,
            color='darkblue',
            opacity=0.8,
            sizemode='diameter'
        ),
        name='Rest'
    ))

    # Add a trace for the top 10% data
    fig.add_trace(go.Scattergeo(
        lat=top_10_percent_data['latitude'],
        lon=top_10_percent_data['longitude'],
        text=top_10_percent_data.apply(lambda row: f"{row['iata_code']}", axis=1),
        hoverinfo='text',
        mode='markers+text',
        textposition='bottom center',
        textfont=dict(color='red'),
        marker=dict(
            size=top_10_percent_data['dummy_values'] / 1000,
            color='red',
            opacity=0.8,
            sizemode='diameter'
        ),
        name='Top 10%'
    ))

    # Rest of the layout code remains the same
    fig.update_layout(
        title='World Map of Airport Coordinates and Dummy Values',
        geo=dict(
            scope='world',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showcountries=True,
            showsubunits=True,
            showocean=True,
            oceancolor='rgb(217, 227, 242)',
            showlakes=True,
            lakecolor='rgb(217, 227, 242)',
            showcoastlines=True,
            coastlinecolor='rgb(204, 204, 204)',
            projection=dict(type='natural earth')
        )
    )

    fig.show()

if __name__ == "__main__":
    csv_url = 'https://datahub.io/core/airport-codes/r/airport-codes.csv'
    airport_codes = get_airport_codes(csv_url)

    # Assuming new_data is a DataFrame with columns 'iata_code' and 'new_values'
    # merged_data = merge_dataframes(airport_codes, new_data)
    # missing_keys = find_missing_keys(airport_codes, new_data)
    # print("Merged DataFrame:")
    # print(merged_data.head())
    # print("Missing IATA Codes:")
    # print(missing_keys)

    # Example: airport_locator
    result = airport_locator(airport_codes, "jfk")
    print(result)

    # Plot the airport map
    plot_airport_map(airport_codes.head(50))
