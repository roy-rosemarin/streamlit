import streamlit as st
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns([2, 4, 2])

from datetime import datetime, timedelta
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import config as cnf
import firebase_database as fbdb
import times
import rooms
import utils
import _thread



def _convert_object_cols_to_boolean(df):
    df[df.columns[df.dtypes == 'object']] = (df[df.columns[df.dtypes == 'object']] == True)
    return df


def _convert_collect_name_to_human_readble(collection_name, st):
    return st.join(collection_name.split('_')[-2:])


def set_date_vars(df, group_by, to_zone=None):
    datetimes = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
    if to_zone != None:
        datetimes = times.change_pd_time_zone(datetimes, 'UTC', to_zone)

    if group_by == 'Date':
        df['Date'] = datetimes.date
    elif group_by == "Hour of Day":
        df['Hour of Day'] = datetimes.hour

    return df


# @st.cache(hash_funcs={plt.figure: lambda _: None}, allow_output_mutation=True, suppress_st_warning=True)
def plot_heatmap(df, group_by, plot_parms, title, xlabel, ylabel, to_zone, scale):
    df = set_date_vars(df, group_by, to_zone=to_zone)
    df_agg = df.groupby(by=[group_by]).mean()

    fmt, vmin, vmax = plot_parms
    fig = plt.figure(figsize=(scale*24, scale*len(df_agg.columns)))
    sns.set(font_scale=scale*2)

    sns.heatmap(df_agg.T.sort_index(), annot=True, annot_kws={"fontsize": scale*16, "weight": "bold"},
                fmt=fmt, linewidths=.5,
                cmap=sns.color_palette("coolwarm", as_cmap=True),
                vmin=vmin, vmax=vmax, cbar=False)

    labels_fontsize = scale * 30
    plt.title(title, fontsize=labels_fontsize) # title with fontsize 20
    plt.xlabel(xlabel, fontsize=labels_fontsize) # x-axis label with fontsize 15
    plt.ylabel(ylabel, fontsize=labels_fontsize) # y-axis label with fontsize 15
    return fig


def get_selectbox_choice(buildnig_data_param):
    rooms_dict = rooms.get_rooms_dict(cnf.room_dict_sites[buildnig_data_param])
    gateway_room_pattern = cnf.gateway_room_dict_sites[buildnig_data_param]
    collect_list = cnf.collect_list_general + cnf.collect_dict_buildings[buildnig_data_param]
    floors_list = [_convert_collect_name_to_human_readble(c, ' ') for c in collect_list]
    floor_param = col2.selectbox('Select floor', floors_list)
    if floor_param not in ('', "All"):
        # choose collection_param from collection_list with same index as the selected floor_param in floors_list
        collection_param = collect_list[floors_list.index(floor_param)]
    elif floor_param == "All":
        collection_param = "All"
    else:
        collection_param = None
    temp_data_param = col2.selectbox('Select A/C data', cnf.temp_data_list)
    aggreg_param = col2.selectbox('Select average by', cnf.aggregation_list)


    return (collect_list, collection_param, temp_data_param,
            floor_param, aggreg_param, rooms_dict, gateway_room_pattern)


def run_flow(db, start_date, end_date, temp_data_param, collection_param, floor_param,
         aggreg_param, to_zone, rooms_dict, gateway_room_pattern, figure_memory_scale):

    df_temps_list, df_states_list = fbdb.get_firebase_data(db,
                                                 collection_param,
                                                 start_date,
                                                 end_date,
                                                 to_zone)

    df_temps = pd.concat(df_temps_list)
    df_states = _convert_object_cols_to_boolean(pd.concat(df_states_list))

    # df_temp_data is pandas dataframes with the pulled data.
    if temp_data_param == "Avg. degrees (°C)":
        df_temp_data = df_temps
        fmt, vmin, vmax = '.1f', 15, 40
    elif temp_data_param == '"On" frequency (%)':
        df_temp_data = df_states
        fmt, vmin, vmax = '0.0%', 0, 1

    if temp_data_param != "":
        df_temp_data = rooms.map_rooms_names(df_temp_data, rooms_dict, gateway_room_pattern)

    if (temp_data_param != "") and (aggreg_param != "") and (collection_param != None):

        fig = plot_heatmap(
            df=df_temp_data,
            group_by=aggreg_param,
            plot_parms=(fmt, vmin, vmax),
            title=floor_param + '\n',
            xlabel='\n' + aggreg_param,
            ylabel='Rooms' + '\n',
            to_zone=to_zone,
            scale=figure_memory_scale)
        col2.write(fig)


def set_title(start_date, end_date):
    #col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.header('TEMPERATURE MONITORING DASHBOARD')
        st.caption(f'Version 1.1, release data: 29/09/2022')
        st.caption(f'Data pulled over the last 7 days between dates: {start_date.date()} - {(end_date-timedelta(days=1)).date()}')
    with col1:
        utils.line_space([col1, col2, col3], [20, 10, 20])
        buildnig_data_param = col1.radio('Select building', cnf.building_list[1:])
    return buildnig_data_param




@st.cache(allow_output_mutation=True, ttl=4*3600, suppress_st_warning=True,
          hash_funcs={_thread.RLock: lambda _: None, dict: lambda _: None})
def set_const_app_settings():
    db = fbdb.get_db_from_textkey()
    start_date = (datetime.today() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
    return db, start_date, end_date


def main():
    db, start_date, end_date = set_const_app_settings()
    buildnig_data_param = set_title(start_date, end_date)
    selectbox_choice = get_selectbox_choice(buildnig_data_param)
    if selectbox_choice:  # if some choice of building has been made
        (collect_list, collection_param, temp_data_param,
         floor_param, aggreg_param, rooms_dict, gateway_room_pattern) = selectbox_choice

        if floor_param not in ('', "All"):
            run_flow(db, start_date, end_date, temp_data_param, collection_param, floor_param,
                 aggreg_param, cnf.to_zone, rooms_dict, gateway_room_pattern, cnf.figure_memory_scale)
        elif floor_param == "All":
                collect_list_BMS = [col for col in collect_list if col not in cnf.collect_list_general][::-1]
                floors_list_BMS = [_convert_collect_name_to_human_readble(c, ' ') for c in collect_list_BMS]

                for i, collection_param in enumerate([col for col in collect_list if col not in cnf.collect_list_general][::-1]):
                    run_flow(db, start_date, end_date, temp_data_param, collection_param, floors_list_BMS[i],
                         aggreg_param, cnf.to_zone, rooms_dict, gateway_room_pattern, cnf.figure_memory_scale)


main()
