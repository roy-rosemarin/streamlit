import rooms
import pandas as pd
import config as cnf
import utils
from datetime import datetime, timedelta
import streamlit as st
import times
import plot
import simulate as sim
import altair as alt
from pytz import timezone
#import scipy


def set_params_exp(col):
    building_param = col.radio('Select Flight', cnf.test_sites, key='experiment_building')
    building_dict = cnf.sites_dict[building_param]
    metric_param = col.radio('Select chart metric',  cnf.metrics, key='experiment_chart_metric')
    time_param = col.radio('Select chart frequency',  cnf.time_agg_dict.keys(), key='experiment_chart_freq')
    return building_param, metric_param, time_param


@st.experimental_singleton(show_spinner=False)
def set_exp_settings(_db, building_param):
    df_dict_param = {}  # dict of structure: {data_param -> floor_param or collection title --> df of all rooms}
    for data_param in cnf.data_param_dict.keys():
        df_dict_param[data_param] = read_data_into_df_dict_param(_db, building_param, data_param)
        building_dict = cnf.sites_dict[building_param]

        for k, v in df_dict_param[data_param].items():
            # transform times of each extracted dataframe
            v_new = transform_times(v, building_dict['time_zone'])
            df_dict_param[data_param][k] = v_new

    df_dict_room = {}  # dict of structure: {floor_param or collection title -> room --> df of all params}
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    for floor_param in building_dict['floors_order']:
        df_dict_room[floor_param] = {}
        for room_param in floor_to_rooms_dict[floor_param]:
            dfs_list = []
            for data_param in cnf.data_param_dict.keys():
                dfs_list += [extract_room_data(df_dict_param[data_param], building_param, data_param, room_param, floor_param)]
            df_dict_room[floor_param][room_param] = utils.join_pandas_df_list(dfs_list)

    return df_dict_room


@st.experimental_singleton(show_spinner=False)
def sim_df_dict(building_param, _df_dict_room, _start_exp_date_utc, _groups=[], _funcs=[]):
    building_dict = cnf.sites_dict[building_param]
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    for group, func in zip(_groups, _funcs):
        for floor_param in building_dict['floors_order']:
            if floor_param in group:
                for room_param in floor_to_rooms_dict[floor_param]:
                    _start_exp_date_utc = _start_exp_date_utc.astimezone(timezone(building_dict['time_zone']))
                    df = _df_dict_room[floor_param][room_param]
                    df1 = df.loc[lambda df: df.index < _start_exp_date_utc]
                    df2 = df.loc[lambda df: df.index >= _start_exp_date_utc]

                    _df_dict_room[floor_param][room_param] = pd.concat([df1, func(df2, 5, building_dict)])

    return _df_dict_room


@st.experimental_singleton(show_spinner=False)
def add_avg_group(building_param, _df_dict_room):
    building_dict = cnf.sites_dict[building_param]
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    for floor_param in building_dict['floors_order']:
        df_list = []
        for room_param in floor_to_rooms_dict[floor_param]:
            df_list += [_df_dict_room[floor_param][room_param]]

        _df_dict_room[floor_param][cnf.num_rooms_field_name] = len(_df_dict_room[floor_param])
        flight_duration = building_dict['end_date_utc'] - building_dict['start_date_utc']
        _df_dict_room[floor_param][cnf.exp_duration_field_name] = f'Flight duration: {flight_duration.days} days ' \
                                                              f'{flight_duration.seconds // 3600} hours ' \
                                                              f'{flight_duration.seconds%3600//60} minutes'

        df_concat = pd.concat(df_list)
        df_sum = df_concat.groupby(df_concat.index).mean()
        df_sum[cnf.elect_consump_name] = ((2.58 / 0.4 / (24*4)) * flight_duration.days
                                          * df_sum['Percentage of A/C usage (%)'])
        df_sum[cnf.elect_cost_name] = 0.136 * df_sum[cnf.elect_consump_name]
        df_sum[cnf.elect_carbon_name] = 0.3381 * df_sum[cnf.elect_consump_name]
        _df_dict_room[floor_param][cnf.avg_group_time_field_name] = df_sum

        t = building_dict['start_exp_date_utc'].astimezone(timezone(building_dict['time_zone']))
        df_sum_pre = df_sum.loc[df_sum.index < t]
        df_sum_post = df_sum.loc[df_sum.index >= t]

        _df_dict_room[floor_param][cnf.avg_pre_field_name] = df_sum_pre.mean()
        _df_dict_room[floor_param][cnf.avg_post_field_name] = df_sum_post.mean()
        _df_dict_room[floor_param][cnf.ste_post_field_name] = df_sum_post.sem()

    return _df_dict_room


def get_rooms_dict(_db, building_param):
    df_dict_room = set_exp_settings(_db, building_param)
    df_dict_room = sim_df_dict(building_param, df_dict_room,
                               _start_exp_date_utc=cnf.sites_dict[building_param]['start_exp_date_utc'],
                               # Apply simulation effect on cnf.sites_dict[building_param]['floors_order'][1:]
                               _groups=[(cnf.sites_dict[building_param]['floors_order'][1:])],
                               _funcs=[sim.sim_test_vent])
    df_dict_room = add_avg_group(building_param, df_dict_room)

    return df_dict_room


def run_summary_exp(df_dict_room, building_param, metric_param, time_param, col):
    floor_dict = df_dict_room[cnf.test_group]
    control_dict = df_dict_room[cnf.control_group]
    # if floor_param == cnf.control_group:
    #     # number of rooms
    #     df_sum = pd.DataFrame([[floor_dict[cnf.num_rooms_field_name]]], index=[cnf.num_rooms_field_name])
    #     df_sum.columns = [floor_param]
    #     # The rest of the metrics
    #     df_sum2 = floor_dict[cnf.avg_post_field_name]
    #     df_sum2 = pd.DataFrame(df_sum2.loc[[i for i in df_sum2.index if 'Outside temperature' not in i]])
    #     df_sum2.columns = [floor_param]
    #     df_sum = df_sum.append(df_sum2)
    # else:
    # number of rooms
    df_sum = pd.DataFrame([[floor_dict[cnf.num_rooms_field_name], control_dict[cnf.num_rooms_field_name]]],
                          index=[cnf.num_rooms_field_name])
    df_sum.columns = [cnf.test_group, cnf.control_group]

    # The rest of the metrics
    df_sum2 = pd.concat([floor_dict[cnf.avg_post_field_name], control_dict[cnf.avg_post_field_name]], axis=1)
    df_sum2 = pd.DataFrame(df_sum2.loc[[i for i in df_sum2.index if 'Outside temperature' not in i]])
    df_sum2.columns = [cnf.test_group, cnf.control_group]
    df_sum2['Difference'] = df_sum2[cnf.test_group] - df_sum2[cnf.control_group]

    df_sum3 = (floor_dict[cnf.avg_group_time_field_name] - control_dict[cnf.avg_group_time_field_name]).sem()
    df_sum3 = pd.DataFrame(df_sum3.loc[[i for i in df_sum3.index if 'Outside temperature' not in i]])
    df_sum3.columns = ['95%  C.I.']
    df_sum2['95%  C.I.'] = df_sum3['95%  C.I.']
    df_sum2['95%  C.I.'] = list(zip(df_sum2['Difference'] - 10*df_sum2['95%  C.I.'], df_sum2['Difference'] + 10*df_sum2['95%  C.I.']))

    df_sum = df_sum.append(df_sum2)

    #df_sum = df_sum.style.highlight_null(props="color: transparent;")
    df_sum = utils.format_row_wise(df_sum, cnf.formatters)

    df_t = (floor_dict[cnf.avg_group_time_field_name][[metric_param]]
                .rename(columns={metric_param: cnf.test_group}))
    #range_ = ['red']
    #if floor_param != cnf.control_group:
    control_col = (control_dict[cnf.avg_group_time_field_name][[metric_param]]
                   .rename(columns={metric_param: cnf.control_group}))
    df_t = df_t.join(control_col)
    range_ = ['red', 'black']

    df_t = df_t.groupby(pd.Grouper(freq=cnf.time_agg_dict[time_param], origin='epoch')).mean()
    df_t.index.name = "Time"
    domain = list(df_t.columns)

    chart = (alt.Chart(df_t.reset_index().melt('Time')).mark_line().encode(
        x=alt.X('Time', axis=alt.Axis(title='', formatType="time", tickColor='white', grid=False, domain=False)),
        y=alt.Y('value', axis=alt.Axis(title='', tickColor='white', domain=False), scale=alt.Scale(zero=False)),
        color=alt.Color('variable',
                        legend=alt.Legend(labelFontSize=14, direction='horizontal', titleAnchor='middle',
                                          orient='bottom', title=''),
                        scale=alt.Scale(domain=domain, range=range_)
                        )
    ))

    # building_dict = cnf.sites_dict[building_param]
    # t = (building_dict['start_exp_date_utc'] - timedelta(hours=25)).astimezone(timezone(building_dict['time_zone']))
    # xrule = (
    #     alt.Chart(pd.DataFrame({'Date': [t]}))
    #     .mark_rule(strokeDash=[12, 6], strokeWidth=2)
    #     .encode(x='Date:T')
    # )


    col.text(floor_dict[cnf.exp_duration_field_name])
    if st.session_state.show_raw_data_experiments:
        col.dataframe(df_t, use_container_width=True)
    else:

        col.table(df_sum)
        col.altair_chart(chart.interactive(), use_container_width=True)


@st.experimental_singleton(show_spinner=False)
def read_data_into_df_dict_param(_db, building_param, data_param):
    building_dict, param_dict = utils.get_config_dicts(building_param, data_param)
    time_param_dict = building_dict  # building_dict has the only required fields start_date_utc and end_date_utc
    collections = building_dict[param_dict['sites_dict_val']]

    df_dict_param = {}
    for i, (collect_name, collect_title) in enumerate(collections):
        df_dict_param.update(utils.get_cooked_df(_db, collect_name, collect_title, building_dict, param_dict, time_param_dict))

    if '' in df_dict_param:
        del df_dict_param['']

    return df_dict_param


def extract_room_data(df_dict, building_param, data_param, room_param, floor_param):
    building_dict, param_dict = utils.get_config_dicts(building_param, data_param)
    collections = building_dict[param_dict['sites_dict_val']]

    if collections == []:
        return pd.DataFrame()
    for i, (collect_name, collect_title) in enumerate(collections):
        if (param_dict['is_rooms']) and (collect_title is not None) and (collect_title != floor_param):
            continue

        if param_dict['is_rooms']:
            df = df_dict[floor_param][[room_param]]
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: data_param})
                break
        else:
            df = df_dict[collect_title]
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: data_param})
    return df


def transform_times(df, time_zone):
    df.index = pd.to_datetime(df.index).round('15min')

    if time_zone is not None:
        df.index = times.change_pd_time_zone(pd.DatetimeIndex(df.index), 'UTC', time_zone)

    df = df.fillna(method="ffill").fillna(method="bfill")
    df = yesterday_to_now(df, time_zone)
    return df


def yesterday_to_now(df, tz):
    local_time_now = times.localise_time_now(tz) - timedelta(minutes=1)
    # localizing to UTC since otherwise altair will change the timezone to browser timezone or utc (which I selected)
    df.index = (df.index + timedelta(days=1))
    return df[df.index <= local_time_now]
