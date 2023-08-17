import pandas as pd
import plotly.graph_objs as go
import random
from datetime import datetime, timedelta

# Global constants
PRODUCTS = ['Product A', 'Product B', 'Product C', 'Product D']
LOCATIONS = ['Location 1', 'Location 2', 'Location 3', 'Location 4']

def create_dataframe(products, locations, date_range):
    df = pd.DataFrame()

    for product in products:
        for location in locations:
            dates = [date_range[0] + timedelta(weeks=i) for i in range((date_range[1]-date_range[0]).days//7+1)]
            df_temp = pd.DataFrame({
                'date': dates,
                'product': [product for _ in range(len(dates))],
                'location': [location for _ in range(len(dates))],
                'value': [random.randint(1, 100) for _ in range(len(dates))],
            })
            df = pd.concat([df, df_temp], ignore_index=True)

    return df

def split_dataframe(df):
    return {name: group for name, group in df.groupby(['product', 'location'])}

def calculate_z_scores(df):
    df_c = df.copy()
    df_c['mean'] = df_c['value'].rolling(window=10).mean()
    df_c['std_dev'] = df_c['value'].rolling(window=10).std()
    df_c['z_score'] = (df_c['value'] - df_c['mean']) / df_c['std_dev']
    return df_c

def trim_values(df):
    df_trimmed = df.copy()
    z_score_trim = 1
    for i in range(-8, 0):
        mean = df_trimmed['mean'].iloc[i]
        std_dev = df_trimmed['std_dev'].iloc[i]
        if df_trimmed['z_score'].iloc[i] > z_score_trim:
            df_trimmed['value'].iloc[i] = mean + z_score_trim * std_dev
        elif df_trimmed['z_score'].iloc[i] < -z_score_trim:
            df_trimmed['value'].iloc[i] = mean - z_score_trim * std_dev
    return df_trimmed


# def plot_timeseries(df, product, location, status):
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines', name='Value'))
#     fig.update_layout(title=f"{product}, {location} - {status}", xaxis_title='Date', yaxis_title='Value')
#     fig.show()
    
def plot_timeseries(df, product, location, status):
    fig = go.Figure()
    # Split the data into two parts based on the specified date
    mask = df['date'] < datetime(2023, 8, 1)
    df_before = df[mask]
    df_after = df[~mask]

    # Create two traces with different colors
    fig.add_trace(go.Scatter(x=df_before['date'], y=df_before['value'], mode='lines', name='Value - Before 8/1/2023', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_after['date'], y=df_after['value'], mode='lines', name='Value - After 8/1/2023', line=dict(color='red')))
    
    # Create a trace to connect the two lines
    if not df_before.empty and not df_after.empty:
        fig.add_trace(go.Scatter(x=[df_before['date'].iloc[-1], df_after['date'].iloc[0]],
                                  y=[df_before['value'].iloc[-1], df_after['value'].iloc[0]],
                                  mode='lines', line=dict(color='blue'), showlegend=False))

    fig.update_layout(title=f"{product}, {location} - {status}", xaxis_title='Date', yaxis_title='Value')
    fig.show()


def plot_z_scores(df, product, location):
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots

    fig = make_subplots()

    # Z-score line
    fig.add_trace(go.Scatter(x=df['date'], y=df['z_score'], mode='lines', name='Z-score'))

    # Z-score Threshold lines
    fig.add_shape(type="line", x0=df['date'].min(), x1=df['date'].max(), y0=1, y1=1, line=dict(color="Red", width=2, dash="dash"), name='+1 Threshold')
    fig.add_shape(type="line", x0=df['date'].min(), x1=df['date'].max(), y0=-1, y1=-1, line=dict(color="Red", width=2, dash="dash"), name='-1 Threshold')

    fig.update_layout(title=f"{product}, {location} - Z-Scores", xaxis_title='Date', yaxis_title='Z-Score', showlegend=True)

    fig.show()

def process_data(df_dict):
    trimmed_dataframes = {}
    for (product, location), df in df_dict.items():
        df_z = calculate_z_scores(df)
        if df_z['z_score'].iloc[-1] > 1:
            print(f"{product} at {location} needs a revision.")
            plot_timeseries(df_z, product, location, "Before Trimming")
            plot_z_scores(df_z, product, location)
            df_trimmed = trim_values(df_z)
            plot_timeseries(df_trimmed, product, location, "After Trimming")
            trimmed_dataframes[(product, location)] = df_trimmed

    return trimmed_dataframes

def main():
    df = create_dataframe(PRODUCTS, LOCATIONS, [datetime.today() - timedelta(weeks=130), datetime.today()])
    df_dict = split_dataframe(df)
    trimmed_dataframes = process_data(df_dict)
    # You can now use or analyze the trimmed_dataframes as needed

main()
