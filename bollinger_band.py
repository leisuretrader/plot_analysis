import base64
from datetime import datetime, timedelta
import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Global constants
PRODUCTS = ['Product A', 'Product B', 'Product C', 'Product D']
LOCATIONS = ['Location 1', 'Location 2', 'Location 3', 'Location 4']

def create_download_button(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    button_id = f"download_button_{filename}"
    return f'<a id="{button_id}" href="data:file/csv;base64,{b64}" download="{filename}.csv">Download {filename} Data</a>'

def split_dataframe(df):
    return {name: group for name, group in df.groupby(['product', 'location'])}

def detect_bb_breach(df):
    return df['value'].iloc[-1] > df['upper_band'].iloc[-1]

def trim_values(df):
    df_original = df.copy()
    original_last_value = df['value'].iloc[-1]

    if detect_bb_breach(df):
        delta_percentage = df['upper_band'].iloc[-1] / df['value'].iloc[-1]
        df['value'] *= delta_percentage
        message = "Data points have been proportionally trimmed down."
    else:
        message = "The last data point has not passed the upper band, no trimming needed."

    adjusted_last_value = df['value'].iloc[-1]
    last_point_difference = original_last_value - adjusted_last_value

    return df, df_original, message, last_point_difference

def calculate_bollinger_bands(df, std_dev_multiplier):
    df_c = df.copy()
    df_c['moving_avg'] = df_c['value'].rolling(window=10).mean()
    df_c['std_dev'] = df_c['value'].rolling(window=10).std()
    df_c['upper_band'] = df_c['moving_avg'] + (df_c['std_dev'] * std_dev_multiplier)
    df_c['lower_band'] = df_c['moving_avg'] - (df_c['std_dev'] * std_dev_multiplier)
    return df_c.dropna()

def plot_bollinger_bands(df, product, location, status):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.date, y=df['value'], mode='lines', name='value'))
    fig.add_trace(go.Scatter(x=df.date, y=df['upper_band'], fill=None, mode='lines', name='upper band'))
    fig.add_trace(go.Scatter(x=df.date, y=df['lower_band'], fill='tonexty', mode='lines', name='lower band'))

    fig.update_layout(title=f'{product}, {location} - {status}')
    
    return fig

def find_products_needing_revision(df_dict):
    return [(product, location) for (product, location), df in df_dict.items() if detect_bb_breach(calculate_bollinger_bands(df, 1))]

def calculate_differences(df_original, df_new):
    df_diff = df_original.copy()
    df_diff['value'] = df_new['value'] - df_original['value']
    return df_diff


###############################################

def initialize_dashboard():
    st.title("Streamlit Bollinger Bands Dashboard")
    df1 = pd.read_csv('hah.csv')
    df1_dict = split_dataframe(df1)
    products_for_revision = find_products_needing_revision(df1_dict)
    
    default_product, default_location = products_for_revision[0] if products_for_revision else (PRODUCTS[0], LOCATIONS[0])

    return df1_dict, default_product, default_location, products_for_revision

def display_product_location_selection(df1_dict, default_product, default_location, products_for_revision):
    product_option = st.selectbox("Choose a product", PRODUCTS, index=PRODUCTS.index(default_product))
    location_option = st.selectbox("Choose a location", LOCATIONS, index=LOCATIONS.index(default_location))

    if (product_option, location_option) in products_for_revision:
        st.write(f"**Note:** {product_option} at {location_option} needs a revision.")

    df = df1_dict[(product_option, location_option)]
    df_bb = calculate_bollinger_bands(df, 1)
    fig = plot_bollinger_bands(df_bb, product_option, location_option, "Original")
    st.plotly_chart(fig)

    if detect_bb_breach(df_bb):
        df_new, df_original, message, _ = trim_values(df_bb)
        st.write(message)
        fig_after = plot_bollinger_bands(df_new, product_option, location_option, "After Trimming")
        st.plotly_chart(fig_after)
        df_diff = calculate_differences(df_original, df_new)
        st.dataframe(df_diff)

    st.write("---")  # Separator

def display_aggregated_data(df1_dict):
    st.header("Part 2: Products & Locations needing revision")
    
    # Aggregate data and create download links
    revision_data = aggregate_revision_data(df1_dict)
    all_data_df = aggregate_all_data(revision_data)
    filename_aggregate = "aggregated_product_location_data"
    download_link_aggregate = create_download_button(all_data_df, filename_aggregate)
    st.markdown(download_link_aggregate, unsafe_allow_html=True)

    for (product, location), (difference, df_original, df_new) in revision_data.items():
        display_revision_data(product, location, df_original, df_new, difference)

def aggregate_revision_data(df1_dict):
    revision_data = {}
    for (product, location), df in df1_dict.items():
        df_bb = calculate_bollinger_bands(df, 1)
        if detect_bb_breach(df_bb):
            df_new, df_original, _, last_point_difference = trim_values(df_bb)
            revision_data[(product, location)] = (last_point_difference, df_original, df_new)
    return dict(sorted(revision_data.items(), key=lambda item: item[1][0], reverse=True))

def aggregate_all_data(sorted_revision_data):
    all_data = []
    for (product, location), (_, df_original, df_new) in sorted_revision_data.items():
        temp_df = df_original.copy()
        temp_df['difference'] = df_new['value'] - df_original['value']
        temp_df['product'] = product
        temp_df['location'] = location
        all_data.append(temp_df)
    return pd.concat(all_data, axis=0)

def display_revision_data(product, location, df_original, df_new, difference):
    st.write(f"**Product:** {product}, **Location:** {location}, **Last Data Point Difference:** {difference:.2f}")

    # Button identifier
    button_id = f"{product}_{location}"

    # Initialize or toggle the state when the button is clicked
    if button_id not in st.session_state:
        st.session_state[button_id] = False

    # Wrap buttons inside a container with side-by-side columns
    col1, col2 = st.columns(2)
    
    # Show/hide button in the first column
    with col1:
        if st.button(f"Show/hide charts for {product} at {location}"):
            st.session_state[button_id] = not st.session_state[button_id]
    
    # CSV Download Link for each product and location in the second column:
    with col2:
        differences_df = df_original.copy()
        differences_df['difference'] = df_new['value'] - df_original['value']
        filename = f"{product}_{location}_data"
        download_button = create_download_button(differences_df, filename)
        st.markdown(download_button, unsafe_allow_html=True)

    # Show charts based on the current state
    if st.session_state[button_id]:
        # Create three columns, the middle column will act as a gap
        col1, gap, col2 = st.columns([0.5, 0.05, 0.5])

        # Set fixed dimensions for the charts
        chart_dimensions = {'height': 400, 'width': 450}

        with col1:  # Use the first column
            st.subheader("Before Trimming")
            fig_original = plot_bollinger_bands(df_original, product, location, "Original")
            fig_original.update_layout(autosize=False, **chart_dimensions)
            st.plotly_chart(fig_original)

        with col2:  # Use the second column
            st.subheader("After Trimming")
            fig_after = plot_bollinger_bands(df_new, product, location, "After Trimming")
            fig_after.update_layout(autosize=False, **chart_dimensions)
            st.plotly_chart(fig_after)

# Main Execution
def main():
    df1_dict, default_product, default_location, products_for_revision = initialize_dashboard()
    display_product_location_selection(df1_dict, default_product, default_location, products_for_revision)
    display_aggregated_data(df1_dict)
    

if __name__ == "__main__":
    main()
