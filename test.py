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
