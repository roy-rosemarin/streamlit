import times
import os
#import logging
#times_log = {}


from streamlit_autorefresh import st_autorefresh
import streamlit as st
st.set_page_config(layout="wide")


import config as cnf
import firebase as fb
import utils
import heatmaps as hmap
import charts as cha
import experiments as exp


# reboot the web app every midnight (UTC timezone) for up to 365 times
count = st_autorefresh(interval=times.milliseconds_until_midnight(), limit=365, key="fizzbuzzcounter")


def set_homepage():
    if 'show_raw_data_charts' not in st.session_state:
        st.session_state.show_raw_data_charts = False
    if 'show_raw_data_heatmaps' not in st.session_state:
        st.session_state.show_raw_data_heatmaps = False
    
    print('*************** last_cache_date:', times.last_cache_date())
    if times.utc_now().strftime('%Y-%m-%d') != times.last_cache_date():
        st.experimental_singleton.clear()
        st.experimental_memo.clear()

    st.header('TEMPERATURE MONITORING DASHBOARD')
    st.caption(f'Version {cnf.app_version}, release data: {cnf.release_date}')

    utils.line_space([st], [1])
    tab1, tab2, tab3 = st.tabs(cnf.tabs)
    utils.line_space([tab1, tab2], [3, 3])
    col11, col12, col13 = tab1.columns([2, 6, 2])
    col21, col22, col23 = tab2.columns([2, 6, 2])
    col31, col32, col33 = tab3.columns([2, 6, 2])
    tab1_building_param, tab1_data_param, tab1_time_param = hmap.set_params_heatmaps(col11)
    tab2_building_param, tab2_floor_param, tab2_room_param = cha.set_params_charts(col21)
    tab3_building_param, tab3_metric_param, tab3_time_param = exp.set_params_exp(col31)
    return (col12, tab1_building_param, tab1_data_param, tab1_time_param,
            col22, tab2_building_param, tab2_floor_param, tab2_room_param,
            col32, tab3_building_param, tab3_metric_param, tab3_time_param)


def main():
    date_today = times.utc_now().strftime("%Y_%m_%d")
    cert_file_path = os.path.join(os.path.realpath('./'), cnf.cert_file)
    db = fb.get_db_from_cert_file(cert_file_path, cnf.storage_bucket)  # Set unchanged settings in the app once

    (col12, tab1_building_param, tab1_data_param, tab1_time_param,
     col22, tab2_building_param, tab2_floor_param, tab2_room_param,
     col32, tab3_building_param, tab3_metric_param, tab3_time_param) = set_homepage()  # Get choice of building
    tab1_building_dict, tab1_param_dict, tab1_time_param_dict = utils.get_config_dicts(tab1_building_param, tab1_data_param, tab1_time_param)

    # # Heatmaps
    # collections = tab1_building_dict[tab1_param_dict['sites_dict_val']]
    # if not collections:
    #     col12.subheader('Sorry. This data is not available for the site.')
    # else:
    #     # hmp_dict structure: {[building_param, data_param, time_param] -> collect_name  -> collect_title else rooms_title -> df of the collection and parameter}
    #     hmp_dict = fb.read_and_unpickle(f'heatmpas_{date_today}', bucket_name=None)
    #     col12.checkbox("Show raw data", value=False, key="show_raw_data_heatmaps")
    #     for collection_df in hmp_dict[tab1_building_param, tab1_data_param, tab1_time_param].values():
    #         hmap.run_plots_heatmaps(collection_df, tab1_building_param, tab1_data_param, tab1_time_param, col12)
    #
    # # Charts
    # col22.checkbox("Show raw data", value=False, key="show_raw_data_charts")
    # # charts_dict structure: {building_param -> floor_param or collection title -> room --> df of all params}
    # charts_dict = fb.read_and_unpickle(f'charts_{date_today}', bucket_name=None)
    # cha.run_flow_charts(charts_dict[tab2_building_param][tab2_floor_param][tab2_room_param], col22)

    # Experiments
    col32.checkbox("Show raw data", value=False, key="show_raw_data_experiments")
    # exp_dict structure: {building_param -> floor_param or collection title -> room --> df of all params}
    exp_dict = fb.read_and_unpickle(f'experiments_{date_today}', bucket_name=None)[tab3_building_param]
    exp_dict = exp.add_avg_group(tab3_building_param, exp_dict)
    exp.run_summary_exp(exp_dict, tab3_building_param, tab3_metric_param, tab3_time_param, col32)


main()
