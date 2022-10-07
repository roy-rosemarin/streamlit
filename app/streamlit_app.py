import streamlit as st
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns([2, 4, 2])

from datetime import datetime, timedelta
import pandas as pd

import config as cnf
import firebase_database as fbdb
import rooms
import plot

# import required for hashing while caching data for streamlit
import utils
import _thread
import google.cloud.firestore_v1.client as gcc


@st.cache(allow_output_mutation=True, ttl=4*3600,
          hash_funcs={dict: lambda _: None, gcc.Client: lambda _: None})
def pull_data(db, start_date, end_date, collect_name, time_zone, param_dict):
    #  Pull data from firebase and convert to pandas DFs
    df_temps_list, df_states_list = fbdb.get_firebase_data(db, collect_name,
                                                           start_date, end_date, time_zone)
    df_temps = pd.concat(df_temps_list)
    df_states = utils.convert_object_cols_to_boolean(pd.concat(df_states_list))

    return df_temps, df_states


@st.cache(allow_output_mutation=True, ttl=4*3600,
          hash_funcs={dict: lambda _: None, gcc.Client: lambda _: None})
def run_flow_rooms(db, start_date, end_date, collect_name, floor_name,
             building_dict, param_dict, aggreg_param):
    rooms_dict = rooms.get_rooms_dict(building_dict['rooms_file'])
    gateway_room_pattern = building_dict['gateway_reg_express']

    df_temps, df_states = pull_data(db, start_date, end_date, collect_name, building_dict['time_zone'], param_dict)

    # df_temp_data is pandas dataframes with the selected data
    if data_param == "Avg. room temperature (°C)":
        df_temp_data = df_temps
    elif data_param == 'Percentage of A/C usage (%)':
        df_temp_data = df_states

    fmt, vmin, vmax = param_dict['fmt'], param_dict['vmin'], param_dict['vmax']

    df_temp_data = rooms.map_rooms_names(df_temp_data, rooms_dict, gateway_room_pattern)

    return plot.plot_heatmap(
        df=df_temp_data,
        group_by=aggreg_param,
        plot_parms=(fmt, vmin, vmax),
        title=floor_name + '\n',
        xlabel=aggreg_param, # '\n' +
        ylabel=f'{floor_name}\nrooms' + '\n',
        to_zone=building_dict['time_zone'],
        scale=cnf.figure_memory_scale)


def set_homepage(start_date, end_date):
    col2.header('TEMPERATURE MONITORING DASHBOARD')
    col2.caption(f'Version {cnf.app_version}, release data: {cnf.release_date}')
    col2.caption(f'Data pulled over the last 7 days between dates: {start_date.date()} - {(end_date-timedelta(days=1)).date()}')
    utils.line_space([col1, col2, col3], [15, 3, 15])
    buildnig_data_param = col1.radio('Select building', cnf.sites_dict.keys())
    data_param = col1.radio('Select data', cnf.data_param_dict.keys())
    aggreg_param = col1.radio('Select average by', cnf.aggregation_list)
    return buildnig_data_param, data_param, aggreg_param


@st.cache(allow_output_mutation=True, ttl=4*3600, suppress_st_warning=True,
          hash_funcs={_thread.RLock: lambda _: None, dict: lambda _: None})
def set_const_app_settings():
    db = fbdb.get_db_from_firebase_key()
    start_date = (datetime.today() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
    return db, start_date, end_date


def main():
    db, start_date, end_date = set_const_app_settings()  # Set unchanged settings in the app once
    buildnig_data_param, data_param, aggreg_param = set_homepage(start_date, end_date)  # Get choice of building
    building_dict = cnf.sites_dict[buildnig_data_param]  # Get building dictionary
    param_dict = cnf.data_param_dict[data_param]  # Get data_param dictionary
    # Get list of collections to query and potentially a list of corresponding floors

    if param_dict['show_rooms']:  # show data by rooms and floors
        (collect_list, floors_list) = (building_dict[param_dict['sites_dict_val']],
                                       building_dict['floor_names'])

        for collect_name, floor_name in zip(collect_list, floors_list):
            fig = run_flow_rooms(db, start_date, end_date, collect_name, floor_name,
                           building_dict, param_dict, aggreg_param)
            col2.write(fig)


main()
