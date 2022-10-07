import streamlit as st
st.set_page_config(layout="wide")
col1, col2, col3 = st.columns([2, 4, 2])

from datetime import datetime, timedelta
import pandas as pd

import config as cnf
import firebase_database as fbdb
import rooms
import plot

import utils
import _thread


def run_flow(db, start_date, end_date, collect_name, floor_name, building_dict, temp_param, aggreg_param):

    rooms_dict = rooms.get_rooms_dict(building_dict['rooms_file'])
    gateway_room_pattern = building_dict['gateway_reg_express']
    to_zone = building_dict['time_zone']

    #  Pull data from firebase and convert to pandas DFs
    df_temps_list, df_states_list = fbdb.get_firebase_data(db, collect_name, start_date, end_date, to_zone)
    df_temps = pd.concat(df_temps_list)
    df_states = utils.convert_object_cols_to_boolean(pd.concat(df_states_list))

    # df_temp_data is pandas dataframes with the selected data
    if temp_param == "Avg. degrees (°C)":
        df_temp_data = df_temps
        fmt, vmin, vmax = '.1f', 15, 40
    elif temp_param == 'Percentage of usage (%)':
        df_temp_data = df_states
        fmt, vmin, vmax = '0.0%', 0, 1

    if temp_param != "":
        df_temp_data = rooms.map_rooms_names(df_temp_data, rooms_dict, gateway_room_pattern)

    if (temp_param != "") and (aggreg_param != ""):

        fig = plot.plot_heatmap(
            df=df_temp_data,
            group_by=aggreg_param,
            plot_parms=(fmt, vmin, vmax),
            title=floor_name + '\n',
            xlabel=aggreg_param, # '\n' +
            ylabel=f'{floor_name}\nrooms' + '\n',
            to_zone=to_zone,
            scale=cnf.figure_memory_scale)
        col2.write(fig)


def set_homepage(start_date, end_date):
    with col2:
        st.header('TEMPERATURE MONITORING DASHBOARD')
        st.caption(f'Version {cnf.app_version}, release data: {cnf.release_date}')
        st.caption(f'Data pulled over the last 7 days between dates: {start_date.date()} - {(end_date-timedelta(days=1)).date()}')
    with col1:
        utils.line_space([col1, col2, col3], [20, 10, 20])
        buildnig_data_param = col1.radio('Select building', cnf.sites_dict.keys())
    return buildnig_data_param


@st.cache(allow_output_mutation=True, ttl=4*3600, suppress_st_warning=True,
          hash_funcs={_thread.RLock: lambda _: None, dict: lambda _: None})
def set_const_app_settings():
    db = fbdb.get_db_from_firebase_key()
    start_date = (datetime.today() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)
    return db, start_date, end_date


def get_selectbox_choice():
    '''
    :return:
    floor_name - the selected floor (corresponding to the above collect_name)
    aggreg_param - the selected aggregation parameter (e.g. daily or hour of day)
    '''
    temp_param = col2.selectbox('Select A/C data', cnf.temp_data_list)
    aggreg_param = col2.selectbox('Select average by', cnf.aggregation_list)
    return temp_param, aggreg_param


def main():
    db, start_date, end_date = set_const_app_settings()  # Set stationary settings
    buildnig_data_param = set_homepage(start_date, end_date)  # Get choice of building
    building_dict = cnf.sites_dict[buildnig_data_param]  # Get building dictionary
    (collect_list, floors_list) = (building_dict['collections'], building_dict['floor_names'])  # Get building collection and floor
    temp_param, aggreg_param = get_selectbox_choice()  # Get other selected parameters
    
    for collect_name, floor_name in zip(collect_list, floors_list):
        run_flow(db, start_date, end_date, collect_name, floor_name, building_dict, temp_param, aggreg_param)


main()
