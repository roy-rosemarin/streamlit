import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import config as cnf
import times

pd.options.mode.chained_assignment = None  # default='warn'
#from natsort import natsort_keygen, ns
#from st_aggrid import AgGrid
#import streamlit as st

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
    cmap = sns.color_palette("coolwarm", as_cmap=True),
    # AgGrid(df_agg.T.reset_index(drop=False, names='rooms')
    #        .sort_index().style
    #        .background_gradient(cmap='bwr', vmin=vmin, vmax=vmax))
    #col.dataframe(df_agg.sort_index().style.hide_index().background_gradient(cmap='bwr', vmin=vmin, vmax=vmax))
    sns.heatmap(df_agg.T.sort_index(), annot=True, annot_kws={"fontsize": scale*16, "weight": "bold"},
                fmt=fmt, linewidths=.5,
                cmap=sns.color_palette("coolwarm", as_cmap=True),
                vmin=vmin, vmax=vmax, cbar=False)

    labels_fontsize = scale * 24
    plt.title(title, fontsize=labels_fontsize) # title with fontsize 20
    plt.xlabel(time_param_dict['aggregation_field_name'], fontsize=labels_fontsize) # x-axis label with fontsize 15
    #plt.ylabel(ylabel, fontsize=labels_fontsize) # y-axis label with fontsize 15
    col.write(fig)
