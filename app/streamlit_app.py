import times
import logging
times_log = {}
logging.info(times.log_time(times_log, 'start'))


from streamlit_autorefresh import st_autorefresh
import streamlit as st
st.set_page_config(layout="wide")

col1, col2, col3 = st.columns([2, 4, 2])
import config as cnf
import firebase_database as fbdb
import rooms
import plot
import utils

# import required for hashing while caching data for streamlit
# import google.cloud.firestore_v1.client as gcc

# reboot the web app every midnight (UTC timezone) for up to 365 times
count = st_autorefresh(interval=1000*times.seconds_until_midnight(), limit=365, key="fizzbuzzcounter")

# @st.cache(allow_output_mutation=True, ttl=4*3600,
#           hash_funcs={dict: lambda _: None, gcc.Client: lambda _: None})
def run_flow_rooms(db, collect_name, collect_title, building_param, data_param, time_param):
    building_dict, param_dict, time_param_dict = utils.get_config_dicts(building_param, data_param, time_param)
    df_pd = fbdb.get_firebase_data(db, collect_name, time_param_dict['start_date_utc'], time_param_dict['end_date_utc'],
                                   param_dict['field_substring'])
    logging.info(times.log_time(times_log, f'got_firebase_data {collect_title}'))
    fmt, vmin, vmax = param_dict['fmt'], param_dict['vmin'], param_dict['vmax']
    if param_dict['is_rooms']:
        rooms_dict = rooms.get_rooms_dict(building_dict['rooms_file'])
        gateway_room_pattern = building_dict['gateway_reg_express']
        df_pd = rooms.map_rooms_names(df_pd.copy(), rooms_dict, gateway_room_pattern)
        logging.info(times.log_time(times_log, f'mapped room names {collect_title}'))
        floors_order_dict = {k: v for v, k in enumerate(building_dict['floors_order'])}
        for rooms_title in sorted(set(df_pd.columns.get_level_values(0)),
                                  key=lambda item: floors_order_dict.get(item, len(floors_order_dict))):
            condition = df_pd.columns.get_level_values(0) == rooms_title
            dff = df_pd.loc[:, condition]
            dff.columns = dff.columns.get_level_values(1)
            logging.info(times.log_time(times_log, f'start_plot {rooms_title}'))
            plot.plot_heatmap(
                df=dff,
                time_param=time_param,
                plot_parms=(fmt, vmin, vmax),
                title=collect_title if collect_title else rooms_title,
                # xlabel=time_param,
                # ylabel=f'{collect_title}\nrooms' + '\n',
                to_zone=building_dict['time_zone'],
                scale=cnf.figure_memory_scale,
                col=col2)
            logging.info(times.log_time(times_log, f'complete_plot {rooms_title}'))
    else:
        logging.info(times.log_time(times_log, f'start_plot {collect_title}'))
        plot.plot_heatmap(
            df=df_pd,
            time_param=time_param,
            plot_parms=(fmt, vmin, vmax),
            title=collect_title,
            #xlabel=time_param,
            #ylabel=f'{collect_title}\nrooms' + '\n',
            to_zone=building_dict['time_zone'],
            scale=cnf.figure_memory_scale,
            col=col2)
        logging.info(times.log_time(times_log, f'complete_plot {collect_title}'))


def set_homepage():
    col2.header('TEMPERATURE MONITORING DASHBOARD')
    col2.caption(f'Version {cnf.app_version}, release data: {cnf.release_date}')
    utils.line_space([col1, col2, col3], [15, 3, 15])
    building_param = col1.radio('Select building', cnf.sites_dict.keys())
    data_param = col1.radio('Select data', cnf.data_param_dict.keys())
    time_param = col1.radio('Select average by', cnf.time_param_dict.keys())
    return building_param, data_param, time_param


def main():
    db = fbdb.get_db_from_firebase_key()  # Set unchanged settings in the app once
    logging.info(times.log_time(times_log, 'fetched_db'))
    building_param, data_param, time_param = set_homepage()  # Get choice of building
    building_dict, param_dict, time_param_dict = utils.get_config_dicts(building_param, data_param, time_param)
    collections = building_dict[param_dict['sites_dict_val']]
    logging.info(times.log_time(times_log, 'fetched_settings'))
    for collect_name, collect_title in collections:
        run_flow_rooms(db, collect_name, collect_title, building_param, data_param, time_param)
        logging.info(times.log_time(times_log, f'flow completed {collect_title}'))



main()
