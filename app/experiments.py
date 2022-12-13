import rooms
import pandas as pd
from datetime import timedelta
import times
import config as cnf
import utils
import streamlit as st
import altair as alt
from pytz import timezone


def set_params_exp(col1, col2):
    building_param = col1.radio('Select Flight', cnf.test_sites, key='exp_building')
    building_dict = cnf.sites_dict[building_param]
    metric_param = col1.radio('Select chart metric',  cnf.metrics, key='exp_chart_metric')
    time_param = col1.radio('Select chart frequency',  cnf.time_agg_dict.keys(), key='exp_chart_freq')
    raw_data = col2.checkbox("Show raw data", value=False, key="exp_raw_data")
    return building_param, metric_param, time_param, raw_data



@st.experimental_memo(show_spinner=False)
def sim_df_dict(building_param, _df_dict_room, _start_exp_date_utc, _groups=[], _funcs=[]):
    building_dict = cnf.sites_dict[building_param]
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'], building_dict['floors_col'])
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


def avg_all_rooms(df_dict_room, floor_to_rooms_dict):
    df_rooms_list = []
    for room_param in floor_to_rooms_dict:
        df_rooms_list += [df_dict_room[room_param]]
    df_concat = pd.concat(df_rooms_list)
    return df_concat.groupby(df_concat.index).mean()


def get_exp_metrics(df_sum, flight_duration):
    df_sum = df_sum.loc[:, [c for c in df_sum.columns if 'Outside temperature' not in c]]
    df_sum[cnf.elect_consump_name] = ((2.58 / 0.4 / (24 * 4)) * flight_duration.days
                                      * df_sum[cnf.ac_usage_name])
    df_sum[cnf.elect_cost_name] = 0.136 * df_sum[cnf.elect_consump_name]
    df_sum[cnf.elect_carbon_name] = 0.3381 * df_sum[cnf.elect_consump_name]
    return df_sum


@st.experimental_memo(show_spinner=False)
def get_exp_summary_dict(building_param, _df_dict_room):
    building_dict = cnf.sites_dict[building_param]
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'], building_dict['floors_col'])
    summary_dict = {}

    # TODO: flight_duration is currently used also for calculations in add_exp_metrics, but otherwise it is not needed
    flight_duration = min(building_dict['end_exp_date_utc'], times.utc_now()) - building_dict['start_exp_date_utc']

    for floor_param in building_dict['floors_order']:
        df_sum = avg_all_rooms(_df_dict_room[floor_param], floor_to_rooms_dict[floor_param])
        df_sum = get_exp_metrics(df_sum, flight_duration)

        t = building_dict['start_exp_date_utc'].astimezone(timezone(building_dict['time_zone']))
        df_sum_pre = df_sum.loc[df_sum.index < t]
        df_sum_post = df_sum.loc[df_sum.index >= t]

        summary_dict[floor_param] = {}
        summary_dict[floor_param][cnf.num_rooms_name] = len(_df_dict_room[floor_param])

        summary_dict[floor_param][cnf.avg_group_df_name] = df_sum
        summary_dict[floor_param][cnf.avg_pre_df_name] = df_sum_pre
        summary_dict[floor_param][cnf.avg_post_df_name] = df_sum_post
    return summary_dict


def _avg_group_series(group_dict):
    return group_dict.mean()


def _se_group_series_absolute(group_dict1, group_dict2):
    return (group_dict1 - group_dict2).sem()


def _se_group_series_relative(pre_dict, post_dict):
    return pre_dict.sem() + post_dict.sem()


def _groups_stats_absolute(test_dict, cont_dict):
    avg_test = _avg_group_series(test_dict)
    avg_cont = _avg_group_series(cont_dict)
    diff = avg_test - avg_cont
    se = _se_group_series_absolute(test_dict, cont_dict)
    return avg_test, avg_cont, diff, se


def _groups_stats_relative(pre_dict, post_dict):
    pre_avg = _avg_group_series(pre_dict)
    post_avg = _avg_group_series(post_dict)
    diff = post_avg / pre_avg - 1
    se = _se_group_series_relative(pre_dict, post_dict)
    return pre_avg, post_avg, diff, se


@st.experimental_memo(show_spinner=False)
def get_exp_summary_df(test_dict, control_dict):
    avg_test, avg_cont, diff, se = _groups_stats_absolute(test_dict, control_dict)
    df_sum = pd.concat([avg_test, avg_cont], axis=1)
    df_sum.columns = [cnf.test_group, cnf.control_group]
    df_sum['Difference'] = diff
    df_sum['95%  C.I.'] = list(zip(diff - 10*se, diff + 10*se))
    return df_sum


@st.experimental_memo(show_spinner=False)
def get_exp_times(building_param):
    building_dict = cnf.sites_dict[building_param]
    start_calibration_date_utc = (building_dict['start_exp_date_utc'] - timedelta(days=building_dict['calibration_days']))
    start_exp_date_utc = min(building_dict['start_exp_date_utc'], times.utc_now())
    end_exp_date_utc = min(building_dict['end_exp_date_utc'], times.utc_now())
    return start_calibration_date_utc, start_exp_date_utc, end_exp_date_utc


@st.experimental_memo(show_spinner=False)
def get_exp_comparison_df(test_pre_dict, test_dict_post_dict, cont_pre_dict, contpost_dict):
    _, _, test_diff, test_se = _groups_stats_relative(test_pre_dict, test_dict_post_dict)
    _, _, cont_diff, cont_se = _groups_stats_relative(cont_pre_dict, contpost_dict)
    df_sum = pd.concat([test_diff, cont_diff], axis=1)
    df_sum.columns = [cnf.test_group, cnf.control_group]
    diff = test_diff - cont_diff
    df_sum['Difference'] = diff
    df_sum['95%  C.I.'] = list(zip(diff - 10*(test_se+cont_se), diff + 10*(test_se+cont_se)))
    return df_sum


def show_summary_tables(_test_dict, _control_dict, _col, building_param):
    start_calibration_date_utc, start_exp_date_utc, end_exp_date_utc = get_exp_times(building_param)
    flight_duration_pre = start_exp_date_utc - start_calibration_date_utc
    flight_duration_post = end_exp_date_utc - start_exp_date_utc

    # Get a comparison stats df between test and control sets
    first_row = pd.DataFrame({cnf.test_group: _test_dict[cnf.num_rooms_name],
                              cnf.control_group: _control_dict[cnf.num_rooms_name]},
                             index=[cnf.num_rooms_name])  # First row with number of rooms

    # The rest of the metrics pre-starting the experiment
    summary_df_pre = get_exp_summary_df(_test_dict[cnf.avg_pre_df_name],
                                            _control_dict[cnf.avg_pre_df_name])
    # The rest of the metrics post-starting the experiment
    summary_df_post = get_exp_summary_df(_test_dict[cnf.avg_post_df_name],
                                             _control_dict[cnf.avg_post_df_name])
    # The rest of the metrics post vs. pre starting the experiment
    summary_df_pre_post = get_exp_comparison_df(_test_dict[cnf.avg_pre_df_name],
                                                _test_dict[cnf.avg_post_df_name],
                                                _control_dict[cnf.avg_pre_df_name],
                                                _control_dict[cnf.avg_post_df_name])

    summary_df_pre = pd.concat([first_row, summary_df_pre])
    summary_df_post = pd.concat([first_row, summary_df_post])
    summary_df_pre_post = pd.concat([first_row, summary_df_pre_post])

    _col.subheader('Pre-experiment calibration results')
    _col.text(f'Pre-experiment calibration duration: {start_calibration_date_utc} - {start_exp_date_utc} '
              f'({flight_duration_pre.days} days) ')
    _col.table(utils.format_row_wise(summary_df_pre, cnf.formatters))
    _col.subheader('Flight period results')
    _col.text(f'Flight duration: {start_exp_date_utc} - {end_exp_date_utc} '
              f'({flight_duration_post.days} days '
              f'{flight_duration_post.seconds // 3600} hours '
              f'{flight_duration_post.seconds%3600//60} minutes)')
    _col.table(utils.format_row_wise(summary_df_post, cnf.formatters))

    _col.subheader('Pre/Post A/B testing results')
    _col.table(utils.format_row_wise(summary_df_pre_post, cnf.formatters2))


@st.experimental_memo(show_spinner=False)
def get_selected_metric_df(_test_dict, _control_dict, building_param, metric_param, time_param):
    df = _test_dict[cnf.avg_group_df_name][[metric_param]].join(
        _control_dict[cnf.avg_group_df_name][[metric_param]],
        lsuffix='_'+cnf.test_group,
        rsuffix='_'+cnf.control_group)
    df = df.groupby(pd.Grouper(freq=cnf.time_agg_dict[time_param], origin='epoch')).mean()
    df.index.name = "Time"
    return df


def chart_df(metric_df, building_param, metric_param):
    range_ = ['red', 'black']
    metric_df.columns = [c.split('_')[-1] for c in metric_df.columns]
    domain = [c.split('_')[-1] for c in metric_df.columns]

    chart = (alt.Chart(metric_df.reset_index().melt('Time'), title=metric_param).mark_line().encode(
        x=alt.X('Time', axis=alt.Axis(title='', formatType="time", tickColor='white', grid=False, domain=False)),
        y=alt.Y('value', axis=alt.Axis(title='', tickColor='white', domain=False), scale=alt.Scale(zero=False)),
        color=alt.Color('variable',
                        legend=alt.Legend(labelFontSize=14, direction='horizontal', titleAnchor='middle',
                                          orient='bottom', title=''),
                        scale=alt.Scale(domain=domain, range=range_)
                        )))

    building_dict = cnf.sites_dict[building_param]
    t = building_dict['start_exp_date_utc'].astimezone(timezone(building_dict['time_zone']))
    xrule = (alt.Chart(pd.DataFrame({'Date': [t]}))
             .mark_rule(strokeDash=[12, 6], strokeWidth=2).encode(x='Date:T', color=alt.value('#7f7f7f')))
    return chart + xrule