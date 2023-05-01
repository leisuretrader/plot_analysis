def get_pct_weights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame with a date column and numerical columns, and returns a new DataFrame
    with the percentage weights of each numerical column per row, rounded to two decimal places.
    Args:
        df: A DataFrame containing a date column and numerical columns.
    Returns:
        A new DataFrame with the percentage weights of each numerical column per row.
    Example:
        data = {'date_time': ['2023-04-01', '2023-04-02', '2023-04-03', '2023-04-04', '2023-04-05'],
                'external': [22, 4, 6, 82, 10],
                'cdo': [32, 6, 29, 12, 15],
                'maws': [44, 82, 12, 162, 20]}
        df = pd.DataFrame(data)
        df2 = calculate_pct_weights(df)

        # df2:
        #             external_pct  cdo_pct  maws_pct
        # date_time                                  
        # 2023-04-01         22.45    32.65     44.90
        # 2023-04-02          4.35     6.52     89.13
        # 2023-04-03         12.77    61.70     25.53
        # 2023-04-04         32.03     4.69     63.28
        # 2023-04-05         22.22    33.33     44.44
    """
    df.set_index(df.columns[0], inplace=True)
    non_date_columns = df.columns    # Get a list of non-date column names
    df['row_sum'] = df[non_date_columns].sum(axis=1)    # Calculate the row sum
    for column in non_date_columns:    # Calculate the percentage weight of each non-date column
        df[f'{column}_pct'] = (df[column] / df['row_sum']) * 100
    df_pct = df[[f'{column}_pct' for column in non_date_columns]]  # Create a new DataFrame with percentage weights
    return df_pct.round(2)

def filter_only_quarterly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame with a date column and numerical columns, and returns a new DataFrame
    with the last non-null value of each quarter for each numerical column.

    Args:
        df: A DataFrame containing a date column and numerical columns.

    Returns:
        A new DataFrame with the last non-null value of each quarter for each numerical column.

    Example:
        See the sample data and result provided in the code below.
        
    eg. 
    data = {'date_time': ['2023-12-02', '2023-02-15', '2023-03-18', '2023-04-01', '2023-06-15', '2023-07-01', '2023-09-30'],
        'internal': [1, 2, 33, 4, 5, 6, 7],
        'external': [22, 4, 26, 8, 10, 12, 14],
        'cdo': [43, 63, 9, 142, 15, 18, 21],
        'maws': [54, 82, 125, 16, 20, 24, 28]}
    sample_df = pd.DataFrame(data)
    result = filter_only_quarterly(sample_df)

    """
    date_column = df.columns[0]  # Get the first column name
    df[date_column] = pd.to_datetime(df[date_column])  # Convert date column to datetime type
    df.set_index(date_column, inplace=True)  # Set date column as the index
    def last_non_null(s):  # Custom function to get the last non-null value in a group
        return s.dropna().iloc[-1]   # Custom function to get the last non-null value in a group-1]
    quarterly_data = df.resample('Q').agg(last_non_null)    # Find the last non-null value of each quarter in the DataFrame
    quarterly_data.reset_index(inplace=True)    # Reset the index to make the date column a regular column
    quarterly_data['quarter'] = quarterly_data[date_column].dt.to_period("Q").astype(str)    # Add a column indicating the calendar quarter
    return quarterly_data 


def add_slope_column(df, window):
    df['date_ordinal'] = pd.to_datetime(df.iloc[:,0]).map(datetime.datetime.toordinal)
    df.reset_index(drop=True, inplace=True)
    # df = df.drop(df.columns[0], axis=1)  #drop the date column since we will use date_ordinal instead
    x_axis = 'date_ordinal'
    df.index = df.iloc[:,1] #df[y_axis] this should be the value column
    df['slope'] = df[x_axis].rolling(window=window).apply(lambda x_axis: linregress(x_axis, x_axis.index)[0])
    return df.reset_index(drop=True).dropna()

def get_slope(df):
    df['date_ordinal'] = pd.to_datetime(df.iloc[:,0]).map(datetime.datetime.toordinal)
    slope, intercept, _, _, _ = linregress(df['date_ordinal'], df.iloc[:,1])
    return slope, intercept

def plot_time_series_with_slope_plotly_single(df):
    slope, intercept = get_slope(df)
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines', name='Time Series'))
    fig.add_trace(go.Scatter(x=df['date'], y=df['date_ordinal'].map(lambda x: slope * x + intercept), mode='lines', name='Slope', line=dict(dash='dot', color='red')))

    fig.update_layout(title='Time Series with Slope Overlay', xaxis_title='Date', yaxis_title='Value')
    fig.show()
