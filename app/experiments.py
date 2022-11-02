import rooms
import pandas as pd
import config as cnf
import utils
from datetime import timedelta
import streamlit as st
import altair as alt
import times
import plot
from sklearn.linear_model import LinearRegression


def set_params_exp(col):
    building_param = col.radio('Select building', cnf.test_sites, key='experiment_building')
    building_dict = cnf.sites_dict[building_param]
    floor_param = col.radio('Select floor', building_dict['floors_order'], key='experiment_floor')
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    room_param = col.selectbox('Select room', sorted(floor_to_rooms_dict[floor_param]), key='experiment_room')
    return building_param, floor_param, room_param


def run_flow_exp(db, building_param, floor_param, room_param, col):
    if col.button('Refresh'):
        st.experimental_singleton.clear()
        st.experimental_memo.clear()

    dfs_list = []
    for data_param in cnf.data_param_dict.keys():
        df_elem, df_dict = loop_over_params(db, building_param, data_param, room_param, floor_param)
        dfs_list += [df_elem]

    df = utils.join_pandas_df_list(dfs_list)
    max_datetime = df.index[-1]

    if st.session_state.show_raw_data_experiments:
        col.dataframe(df, use_container_width=True)
    else:
        if col.checkbox("Show simulated line", value=floor_param in cnf.sites_dict[building_param]['floors_order'][1:3]):


            '''
            # Code for regression based simulation 
            X = df.iloc[:, :0]
            y = df.iloc[:, :0]

            y['temp_diff'] = df["Avg. room temperature (°C)"].shift(-1).diff()
            X["diff2outside"] = df["Avg. room temperature (°C)"] - df["Outside temperature (°C)"]
            X["pos_diff2outside"] = X["diff2outside"].clip(lower=0, upper=None)
            X["neg_diff2outside"] = - X["diff2outside"].clip(lower=None, upper=0)
            X["diff2ac"] = df['Percentage of A/C usage (%)'] * (df["Avg. room temperature (°C)"]
                                                                  - df["Cooling temperature set point (°C)"])
            X["pos_diff2ac"] = X["diff2ac"].clip(lower=0, upper=None)
            X["neg_diff2ac"] = - neg_diff2outside.clip(lower=None, upper=0)

            reg = LinearRegression().fit(X, y)
            print(reg.coef_)
            print(reg.predict(X))  # make predictions
            '''

            df2 = df.copy()
            df2 = shrink_ac_usage(df2)
            df2 = shrink_ac_usage(df2)
            diff2outside = df2["Avg. room temperature (°C)"] - df2["Outside temperature (°C)"]
            pos_diff2outside = diff2outside.clip(lower=0, upper=None)
            neg_diff2outside = - diff2outside.clip(lower=None, upper=0)
            diff2ac = df2["Avg. room temperature (°C)"] - df2["Cooling temperature set point (°C)"]
            pos_diff2ac = diff2ac.clip(lower=0, upper=None)
            neg_diff2ac = - diff2ac.clip(lower=None, upper=0)
            ac_on = df2['Percentage of A/C usage (%)']
            ac_off = 1 - ac_on

            df2["Avg. room temperature (°C)"] = (ac_on * (df2["Avg. room temperature (°C)"]
                                                          - 0.3 * pos_diff2ac - 0.1 * pos_diff2outside)
                                                 + ac_off * (0.97 * df2["Avg. room temperature (°C)"]
                                                             - 0.1 * pos_diff2outside))

            col.altair_chart(charts(df2, max_datetime).interactive(), use_container_width=True)
        else:
            col.altair_chart(charts(df, max_datetime).interactive(), use_container_width=True)


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
            print('$$$$$$$$$$$$$$', building_param, data_param, room_param, floor_param)
            print(df_dict[floor_param])
            df = df_dict[floor_param][[room_param]]
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: data_param})
        else:
            df = df_dict[collect_title]
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: data_param})

        df.index = pd.to_datetime(df.index).round('15min')

    if building_dict['time_zone'] is not None:
        df.index = times.change_pd_time_zone(df.index, 'UTC', building_dict['time_zone'])

    # TODO: keep this only for pitch
    df = df.fillna(method="ffill")
    df = yesterday_to_now(df, building_dict['time_zone'])

    return df, df_dict


def yesterday_to_now(df, tz):
    local_time_now = times.localise_time_now(tz) - timedelta(minutes=1)
    # localizing to UTC since otherwise altair will change the timezone to browser timezone or utc (which I selected)
    df.index = (df.index + timedelta(days=1))
    return df[df.index <= local_time_now]


def charts(df, _max_datetime):
    # TODO: Ugly code. Must improve this code, no need for a separate chart for predictions
    df_on_off_times = plot.create_start_end_times(df, 'Percentage of A/C usage (%)')
    pred_row = pd.DataFrame([[None]*len(df.columns)], columns=df.columns, index=[_max_datetime+timedelta(hours=3)])
    pred_row['Outside temperature (°C)'] = df.iloc[-1]['_Outside temperature 3h prediction (°C)']
    df = pd.concat([df, pred_row])

    xvars = [col for col in df.columns if
             col not in ('Percentage of A/C usage (%)', '_Outside temperature 3h prediction (°C)')]
    df.index.name = "Time"
    df = df[xvars].reset_index().melt('Time')
    domain = xvars
    if len(df.columns) == 2:
        range_ = ['black', 'burlywood']
    else:
        range_ = ['black', 'lightskyblue', 'burlywood']

    chart = (alt.Chart(df.loc[df['Time'] <= _max_datetime]).mark_line(
        #    strokeDash=alt.condition(f'datum.Time < {max_datetime}', [0], [1, 1])
    ).encode(
        x=alt.X('Time', axis=alt.Axis(title='', formatType="time", tickColor='white', grid=False, domain=False)),
        y=alt.Y('value', axis=alt.Axis(title='', tickColor='white', domain=False), scale=alt.Scale(zero=False)),
        color=alt.Color('variable',
                        legend=alt.Legend(labelFontSize=14, direction='horizontal', titleAnchor='middle',
                                          orient='bottom', title=''),
                        scale=alt.Scale(domain=domain, range=range_)
                        )
    ))

    pred_chart = (alt.Chart(df.loc[df['Time'] >= _max_datetime]).mark_line(strokeDash=[1, 1]).encode(
        x=alt.X('Time', axis=alt.Axis(title='', formatType="time", tickColor='white', grid=False, domain=False)),
        y=alt.Y('value', axis=alt.Axis(title='', tickColor='white', domain=False)),
        color=alt.Color('variable',
                        legend=alt.Legend(labelFontSize=14, direction='horizontal', titleAnchor='middle',
                                          orient='bottom', title=''),
                        scale=alt.Scale(domain=domain, range=range_)
                        )
    ))

    rect = alt.Chart(df_on_off_times).mark_rect().mark_rect(opacity=0.2).encode(
        x='start_on_times:T',
        x2='end_on_times:T'
    )
    ch_lay = alt.layer(chart, pred_chart, rect).configure_view(strokeWidth=0)  # chart, pred_chart, rect
    return ch_lay


def shrink_ac_usage(df):
    prev_row = df.iloc[0, :]
    for index, row in df.iterrows():
        if ((row['Percentage of A/C usage (%)'] and not prev_row['Percentage of A/C usage (%)'] > 0) and
                (row["Avg. room temperature (°C)"] - prev_row["Avg. room temperature (°C)"] >= 0)):
            df.at[index, 'Percentage of A/C usage (%)'] = False
        prev_row = row

    prev_row = df.iloc[-1, :]
    for index, row in df[::-1].iterrows():
        if ((row['Percentage of A/C usage (%)'] and not prev_row['Percentage of A/C usage (%)'] > 0) and
                (row["Avg. room temperature (°C)"] - prev_row["Avg. room temperature (°C)"] >= 0)):
            df.at[index, 'Percentage of A/C usage (%)'] = False
        prev_row = row
    return df
