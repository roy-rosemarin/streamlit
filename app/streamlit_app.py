from streamlit_autorefresh import st_autorefresh
import streamlit as st
st.set_page_config(layout="wide")


import config as cnf
import times
import firebase_database as fbdb
import utils
import heatmaps as hmap
import charts as cha


# reboot the web app every midnight (UTC timezone) for up to 365 times
count = st_autorefresh(interval=times.milliseconds_until_midnight(), limit=365, key="fizzbuzzcounter")


def set_homepage():
    st.header('TEMPERATURE MONITORING DASHBOARD')
    st.caption(f'Version {cnf.app_version}, release data: {cnf.release_date}')
    utils.line_space([st], [1])
    tab1, tab2 = st.tabs(cnf.tabs)
    utils.line_space([tab1, tab2], [3, 3])
    col11, col12, col13 = tab1.columns([2, 6, 2])
    col24, col25, col26 = tab2.columns([2, 6, 2])
    tab1_building_param, tab1_data_param, tab1_time_param = hmap.set_params(col11)
    tab2_building_param, tab2_floor_param, tab2_room_param = cha.set_params(col24)
    return (col12, tab1_building_param, tab1_data_param, tab1_time_param,
            col25, tab2_building_param, tab2_floor_param, tab2_room_param)


def main():
    db = fbdb.get_db_from_firebase_key()  # Set unchanged settings in the app once
    (col12, tab1_building_param, tab1_data_param, tab1_time_param,
     col25, tab2_building_param, tab2_floor_param, tab2_room_param) = set_homepage()  # Get choice of building
    tab1_building_dict, tab1_param_dict, tab1_time_param_dict = utils.get_config_dicts(tab1_building_param, tab1_data_param, tab1_time_param)
    collections = tab1_building_dict[tab1_param_dict['sites_dict_val']]

    for i, (collect_name, collect_title) in enumerate(collections):
        hmap.run_flow_heatmaps(db, collect_name, collect_title, tab1_building_param, tab1_data_param, tab1_time_param, col12)
        if cnf.test and (i == 0):
            break

    cha.run_flow_charts(col25)



main()
