import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import config as cnf
import times
from datetime import timedelta
import streamlit as st

plt.rcParams.update({'figure.max_open_warning': 0})
pd.options.mode.chained_assignment = None  # default='warn'


def set_date_vars(df, time_param_dict, to_zone=None):

    datetime_col = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
    if to_zone is not None:
        datetime_col = times.change_pd_time_zone(datetime_col, 'UTC', to_zone)

    aggregation_field_name = time_param_dict['aggregation_field_name']
    aggregation_strftime = time_param_dict['aggregation_strftime']
    df[aggregation_field_name] = datetime_col.strftime(aggregation_strftime)
    return df.groupby(by=[aggregation_field_name]).mean()


def plot_heatmap(df, time_param, plot_parms, title, to_zone, scale, col):
    time_param_dict = cnf.time_param_dict[time_param]
    df_agg = set_date_vars(df, time_param_dict, to_zone=to_zone)
    fmt, vmin, vmax = plot_parms
    fig = plt.figure(figsize=(scale*24, scale*len(df_agg.columns)))
    sns.set(font_scale=scale*2)

    if st.session_state.show_raw_data_heatmaps:
        col.header(title)
        col.dataframe(df_agg.sort_index())
    else:
        df_plot = df_agg.T.sort_index()
        sns.heatmap(df_plot,
                    annot=True, annot_kws={"fontsize": scale*16, "weight": "bold"},
                    fmt=fmt, linewidths=.5,
                    cmap=sns.color_palette("coolwarm", as_cmap=True),
                    vmin=vmin, vmax=vmax, cbar=False)

        labels_fontsize = scale * 24
        plt.title(title, fontsize=labels_fontsize)  # title with fontsize 20
        plt.xlabel(time_param_dict['aggregation_field_name'], fontsize=labels_fontsize)  # x-axis label with fontsize 15
        #plt.ylabel(ylabel, fontsize=labels_fontsize) # y-axis label with fontsize 15
        plt.yticks(rotation=0)
        col.write(fig)


@st.experimental_singleton(show_spinner=False)
def create_start_end_times(df, col_name):
    column = df[col_name]
    start_on_times = []
    end_on_times = []
    if column.iloc[0]:
        start_on_times += [list(df.index)[0]]
    if column.iloc[-1]:
        end_on_times += [list(df.index)[-1]]

    start_on_times = start_on_times + list(df[(column - column.shift(1)) > 0].index)
    end_on_times = list(df[(column - column.shift(-1)) > 0].index) + end_on_times
    start_on_times = [t - timedelta(minutes=7.5) for t in start_on_times]
    end_on_times = [t + timedelta(minutes=7.5) for t in end_on_times]
    return pd.DataFrame({'start_on_times': start_on_times, 'end_on_times': end_on_times})
