def add_slope(df, window, x_axis, y_axis):
    df = df.reset_index()
    df['date_ordinal'] = pd.to_datetime(df.iloc[:,0]).map(datetime.datetime.toordinal)
    df = df.drop(df.columns[0], axis=1)  #drop the date column since we will use date_ordinal instead
    x_axis = df.iloc[:,1]
    y_axis = df.iloc[:,0]  #this should be the date_ordinal column
    df.index = df[y_axis]
    df['slope'] = df[x_axis].rolling(window=window).apply(lambda x_axis: linregress(x_axis, x_axis.index)[0])
    return df.reset_index(drop=True)
