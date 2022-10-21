import config as cnf
import times
import streamlit as st
import firebase_database as fbdb
import rooms
import google.cloud.firestore_v1.client as gcc
import functools as ft
import pandas as pd


def line_space(cols_list, lines_list):
    for col, lines in zip(cols_list, lines_list):
        for i in range(lines):
            col.text("")


def convert_object_cols_to_boolean(df):
    df[df.columns[df.dtypes == 'object']] = (df[df.columns[df.dtypes == 'object']] is True)
    return df


@st.experimental_singleton(show_spinner=False)
def get_config_dicts(building_param, data_param, time_param=None):
    building_dict = cnf.sites_dict[building_param]
    param_dict = cnf.data_param_dict[data_param]
    if time_param:
        time_param_dict = cnf.time_param_dict[time_param]
        return building_dict, param_dict, time_param_dict
    else:
        return building_dict, param_dict


@st.experimental_singleton(show_spinner=False)
def join_pandas_df_list(dfs_list):
    return ft.reduce(lambda left, right: left.join(right, how='left'), dfs_list)


@st.experimental_singleton(show_spinner=False)
def get_cooked_df(_db, collect_name, collect_title, building_dict, param_dict, time_param_dict):
    df_dict = {}

    df_pd = fbdb.get_firebase_data(_db, collect_name, time_param_dict['start_date_utc'], time_param_dict['end_date_utc'],
                                   param_dict['field_keyword'], param_dict['match_keyword'])

    if param_dict['is_rooms']:
        rooms_dict = rooms.get_code_to_room_dict(building_dict['rooms_file'])
        gateway_room_pattern = building_dict['gateway_reg_express']
        df_pd = rooms.map_rooms_names(df_pd.copy(), rooms_dict, gateway_room_pattern)
        floors_order_dict = {k: v for v, k in enumerate(building_dict['floors_order'])}
        for rooms_title in sorted(set(df_pd.columns.get_level_values(0)),
                                  key=lambda item: floors_order_dict.get(item, len(floors_order_dict))):
            condition = df_pd.columns.get_level_values(0) == rooms_title
            dff = df_pd.loc[:, condition]
            dff.columns = dff.columns.get_level_values(1)
            df_dict[collect_title if collect_title else rooms_title] = dff
    else:
        df_dict[collect_title] = df_pd
    return df_dict
