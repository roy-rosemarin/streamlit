import rooms
import pandas as pd
import config as cnf
import utils
from datetime import datetime, timedelta
import time
import streamlit as st
import altair as alt
import times


def set_params_charts(col):
    building_param = col.radio('Select building', cnf.sites_dict.keys(), key='chart')
    building_dict = cnf.sites_dict[building_param]
    floor_param = col.radio('Select floor', building_dict['floors_order'])
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    room_param = col.selectbox('Select room', sorted(floor_to_rooms_dict[floor_param]))
    return building_param, floor_param, room_param


def run_flow_charts(db, building_param, floor_param, room_param, col):
    last_time = time.time()
    dfs_list = []
    for data_param in cnf.data_param_dict.keys():
        dfs_list += [loop_over_params(db, building_param, data_param, room_param, floor_param)]

    df = utils.join_pandas_df_list(dfs_list)

    column = df['Percentage of A/C usage (%)']
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
    df2 = alt.pd.DataFrame({'start_on_times': start_on_times, 'end_on_times': end_on_times})
    print(df2)

    if st.session_state.show_raw_data_charts:
        col.dataframe(df)
    else:
        xvars = [col for col in df.columns if col != 'Percentage of A/C usage (%)']
        df.index.name = "Time"
        df = df[xvars].reset_index().melt('Time')
        domain = xvars
        range_ = ['blue', 'lightskyblue', 'red', 'burlywood']
        chart = (alt.Chart(df).mark_line().encode(
            x=alt.X('Time', axis=alt.Axis(title='', formatType="time", tickColor='white', grid=False, domain=False)),
            y=alt.Y('value', axis=alt.Axis(title='', tickColor='white', domain=False)),
            color=alt.Color('variable',
                            legend=alt.Legend(labelFontSize=14, direction='horizontal', titleAnchor='middle', orient='bottom', title=''),
                            scale=alt.Scale(domain=domain, range=range_)
                            )
        ))

        rect = alt.Chart(df2).mark_rect().encode(
            x='start:T',
            x2='end:T'
        )
        ch_lay = alt.layer(chart, rect).configure_view(strokeWidth=0)
        col.altair_chart(ch_lay.interactive(), use_container_width=True)
    current_time = time.time()
    print(current_time - last_time, "seconds")


def loop_over_params(db, building_param, data_param, room_param, floor_param):
    building_dict, param_dict = utils.get_config_dicts(building_param, data_param)
    time_param_dict = cnf.time_param_dict["Date (last 7 days)"]
    # {'start_date_utc': (datetime.utcnow() - timedelta(days=7)), 'end_date_utc': (datetime.utcnow())}
    collections = building_dict[param_dict['sites_dict_val']]
    for i, (collect_name, collect_title) in enumerate(collections):
        if (param_dict['is_rooms']) and (collect_title is not None) and (collect_title != floor_param):
            continue

        df_dict = utils.get_cooked_df(db, collect_name, collect_title, building_dict, param_dict, time_param_dict)
        if param_dict['is_rooms']:
            df = df_dict[floor_param][[room_param]]
            df = df.rename(columns={df.columns[0]: data_param})
        else:
            df = df_dict[collect_title]
            df = df.rename(columns={df.columns[0]: collect_title})

        df.index = pd.to_datetime(df.index).round('15min')

    if building_dict['time_zone'] is not None:
        df.index = times.change_pd_time_zone(df.index, 'UTC', building_dict['time_zone'])

    # TODO: keep this only for pitch
    df = yesterday_to_now(df, building_dict['time_zone'])

    return df


def yesterday_to_now(df, tz):
    local_time_now = times.localise_time_now(tz) - timedelta(minutes=1)
    # localizing to UTC since otherwise altair will change the timezone to browser timezone or utc (which I selected)
    df.index = (df.index + timedelta(days=1))
    return df[df.index <= local_time_now]
