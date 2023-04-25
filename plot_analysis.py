import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class PlotAnalysis:
    def __init__(self):
        pass

    def dummy_value(self):
        dates = pd.date_range(start='2023-04-24', periods=100, freq='D')
        integers = np.random.randint(0, 100, 100)
        df = pd.DataFrame({'Date': dates, 'Value': integers})
        return df

    def perc_change(self, df, horizon, column_index=1, keep_only_perc_change=True):
        horizon = horizon-1
        df['perc_change'] = df.iloc[:,column_index].pct_change(periods=horizon,fill_method='ffill').round(decimals=4)
        if keep_only_perc_change ==True:
            return df.drop(df.columns[1],axis=1).dropna()
        else:
            return df.dropna()

    def describe_df(self, df, column_index=1):
        return df.iloc[:,column_index].describe(percentiles = [.001,.01,.05,.1,.15,.25,.5,.75,.85,.90,.95,.99,.999]).round(2).reset_index()

    def describe_df_forecast(self, df, input_value, column_index=1):
        describe = self.describe_df(df, column_index)
        describe['input_value'] = input_value
        describe['forecast_value'] = input_value * (1+describe.iloc[:,column_index]/100).round(3)
        return describe

    def plot_describe_df(self, describe_df):
        fig = go.Figure(data=[go.Table(header=dict(values=describe_df.columns.tolist()),
                        cells=dict(values=[describe_df.iloc[:,0].tolist(), 
                                           describe_df.iloc[:,1].tolist(),
                                           ]))])
        fig.show()

    def plot_ts_line_chart(self, df, y_values=None):
        if df.index.name is None: 
            trace = go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1], mode='lines')
        else:
            trace = go.Scatter(x=df.index, y=df.iloc[:,1], mode='lines')
        data = [trace]

        if y_values is not None:
            for y in y_values:
                horizontal_line = go.Scatter(x=[df.iloc[0, 0], df.iloc[-1, 0]], y=[y, y], mode='lines', line=dict(color='red', dash='dash'))
                data.append(horizontal_line)

        layout = go.Layout(title='Time Series Data Movement', xaxis_title='Date', yaxis_title='Value')
        fig = go.Figure(data=data, layout=layout)
        fig.show()

    def plot_count_frequency_histogram(self, df, column_index=1, second_window=None, show_latest_value=True):
        fig = go.Figure()
        second_column_dt = df.iloc[:, column_index].dtype
        if second_column_dt != np.dtype('int64') and second_column_dt != np.dtype('float64'):
            raise Exception("The data type of the second column is not integer or float. Please make sure the second column is an integer or float.")
        else:
            value_column = df.iloc[:, column_index].values.tolist()
            fig.add_trace(go.Histogram(x=value_column,
                                       name='all records',
                                       marker_color='#330C73',
                                       opacity=0.75))

            if second_window is not None:
                latest_perc_change_l = value_column[-second_window:]
                fig.add_trace(go.Histogram(x=latest_perc_change_l,
                                           name='last {}'.format(second_window),
                                           marker_color='#EB89B5',
                                           opacity=0.9))
            else:
                pass

            if show_latest_value:
                cur_per_change = value_column[-1:]
                fig.add_trace(go.Histogram(x=cur_per_change,
                                           name='latest',
                                           marker_color='#FF0000',
                                           opacity=1))
            else:
                pass

            fig.update_layout(
                barmode='overlay',
                title_text='Distribution Count - (time count : {})'.format(len(df)),
                xaxis_title_text='Value',
                yaxis_title_text='Frequency Count',
            )
            fig.show()
