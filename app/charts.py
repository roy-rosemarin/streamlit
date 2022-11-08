import rooms
import pandas as pd
import config as cnf
import utils
from datetime import timedelta
import streamlit as st
import times
import plot


def set_params_charts(col):
    building_param = col.radio('Select building', cnf.non_test_sites, key='chart_building')
    building_dict = cnf.sites_dict[building_param]
    floor_param = col.radio('Select floor', building_dict['floors_order'], key='chart_floor')
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    room_param = col.selectbox('Select room', sorted(floor_to_rooms_dict[floor_param]), key='chart_room')
    return building_param, floor_param, room_param


def run_flow_charts(db, building_param, floor_param, room_param, col):
    dfs_list = []
    for data_param in cnf.data_param_dict.keys():
        dfs_list += [loop_over_params(db, building_param, data_param, room_param, floor_param)]

    df = utils.join_pandas_df_list(dfs_list)
    max_datetime = df.index[-1]
    if st.session_state.show_raw_data_charts:
        col.dataframe(df, use_container_width=True)
    else:
        col.altair_chart(plot.charts(df, max_datetime).interactive(), use_container_width=True)


def loop_over_params(db, building_param, data_param, room_param, floor_param):
    building_dict, param_dict = utils.get_config_dicts(building_param, data_param)
    time_param_dict = cnf.time_param_dict["Date (last 7 days)"]
    collections = building_dict[param_dict['sites_dict_val']]
    if collections == []:
        return pd.DataFrame()
    for i, (collect_name, collect_title) in enumerate(collections):
        if (param_dict['is_rooms']) and (collect_title is not None) and (collect_title != floor_param):
            continue

        df_dict = utils.get_cooked_df(db, collect_name, collect_title, building_dict, param_dict, time_param_dict)
        if param_dict['is_rooms']:
            df = df_dict[floor_param][[room_param]]
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: data_param})
        else:
            df = df_dict[collect_title]
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: data_param})

        df.index = pd.to_datetime(df.index).round('15min')

    if building_dict['time_zone'] is not None:
        df.index = times.change_pd_time_zone(pd.DatetimeIndex(df.index), 'UTC', building_dict['time_zone'])

    # TODO: keep this only for pitch
    df = df.fillna(method="ffill").fillna(method="bfill")
    df = yesterday_to_now(df, building_dict['time_zone'])

    return df


def yesterday_to_now(df, tz):
    local_time_now = times.localise_time_now(tz) - timedelta(minutes=1)
    # localizing to UTC since otherwise altair will change the timezone to browser timezone or utc (which I selected)
    df.index = (df.index + timedelta(days=1))
    return df[df.index <= local_time_now]
