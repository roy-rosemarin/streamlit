from datetime import datetime, timedelta
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

import config as cnf
import firebase_database as fbdb
import times
import rooms

import _thread


def _convert_object_cols_to_boolean(df):
    df[df.columns[df.dtypes == 'object']] = (df[df.columns[df.dtypes == 'object']] == True)
    return df


def set_date_vars(df, group_by, to_zone=None):
    datetimes = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
    if to_zone != None:
        datetimes = times.change_pd_time_zone(datetimes, 'UTC', to_zone)

    if group_by == 'Date':
        df['Date'] = datetimes.date
    elif group_by == "Hour of Day":
        df['Hour of Day'] = datetimes.hour

    return df


# @st.cache(hash_funcs={plt.figure: lambda _: None}, allow_output_mutation=True, suppress_st_warning=True)
def plot_heatmap(df, group_by, plot_parms, title, xlabel, ylabel, to_zone, scale):
    df = set_date_vars(df, group_by, to_zone=to_zone)
    df_agg = df.groupby(by=[group_by]).mean()

    fmt, vmin, vmax = plot_parms
    fig = plt.figure(figsize=(scale*24, scale*len(df_agg.columns)))
    sns.set(font_scale=scale*2)

    sns.heatmap(df_agg.T.sort_index(), annot=True, annot_kws={"fontsize": scale*16, "weight": "bold"},
                fmt=fmt, linewidths=.5,
                cmap=sns.color_palette("coolwarm", as_cmap=True),
                vmin=vmin, vmax=vmax, cbar=False)

    labels_fontsize = scale * 30
    plt.title(title, fontsize=labels_fontsize) # title with fontsize 20
    plt.xlabel(xlabel, fontsize=labels_fontsize) # x-axis label with fontsize 15
    plt.ylabel(ylabel, fontsize=labels_fontsize) # y-axis label with fontsize 15
    return fig


def get_selectbox_choice(temp_data_list, floors_list, aggregation_list):
    temp_data_param = st.selectbox('A/C data', temp_data_list)
    floor_param = st.selectbox('Floor', floors_list)
    if floor_param not in ('Select floor', "All"):
        collection_param = f'BMS_Malaga_Climatizacion_{floor_param}'
    elif floor_param == "All":
        collection_param = "All"
    else:
        collection_param = None

    aggreg_param = st.selectbox('Average by', aggregation_list)

    return collection_param, temp_data_param, floor_param, aggreg_param


def run_flow(db, start_date, end_date, temp_data_param, collection_param, floor_param,
         aggreg_param, to_zone, rooms_dict, figure_memory_scale):

    df_temps_list, df_states_list = fbdb.get_firebase_data(db,
                                                 collection_param,
                                                 start_date,
                                                 end_date,
                                                 to_zone)

    df_temps = pd.concat(df_temps_list)
    df_states = _convert_object_cols_to_boolean(pd.concat(df_states_list))

    # df_temp_data is pandas dataframes with the pulled data.
    if temp_data_param == "Avg. degrees (°C)":
        df_temp_data = df_temps
        fmt, vmin, vmax = '.1f', 15, 40
    elif temp_data_param == '"On" frequency (%)':
        df_temp_data = df_states
        fmt, vmin, vmax = '0.0%', 0, 1

    if temp_data_param != "Select A/C data":
        df_temp_data = rooms.map_rooms_names(df_temp_data, rooms_dict)

    if (temp_data_param != "Select A/C data") and (aggreg_param != "Select aggregation by") and (collection_param != None):

        fig = plot_heatmap(
            df=df_temp_data,
            group_by=aggreg_param,
            plot_parms=(fmt, vmin, vmax),
            title=floor_param + '\n',
            xlabel='\n' + aggreg_param,
            ylabel='Rooms' + '\n',
            to_zone=to_zone,
            scale=figure_memory_scale)
        st.write(fig)


@st.cache(allow_output_mutation=True, ttl=4*3600,
          hash_funcs={_thread.RLock: lambda _: None, dict: lambda _: None})
def set_app_settings():
    db = fbdb.get_db_from_textkey()
    start_date = (datetime.today() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)

    rooms_dict = rooms.get_rooms_dict(cnf.rooms_mapping_file)
    collect_list = cnf.collect_list_general + cnf.collect_list_malaga
    floors_list = [c.replace('BMS_Malaga_Climatizacion_', '') for c in collect_list]

    return db, start_date, end_date, rooms_dict, collect_list, floors_list


def main():
    db, start_date, end_date, rooms_dict, collect_list, floors_list = set_app_settings()

    st.header('MALAGA AIR CONDITIONING HEATMAPS')
    st.caption(f'Version 1.0, release data: 16/09/2022')
    st.caption(f'Data pulled over the last 7 days between dates: {start_date.date()} - {(end_date-timedelta(days=1)).date()}')

    collection_param, temp_data_param, floor_param, aggreg_param = \
        get_selectbox_choice(cnf.temp_data_list, tuple(floors_list), cnf.aggregation_list)

    if floor_param not in ('Select floor', "All"):
        run_flow(db, start_date, end_date, temp_data_param, collection_param, floor_param,
             aggreg_param, cnf.to_zone, rooms_dict, cnf.figure_memory_scale)
    elif floor_param == "All":
        collect_list_BMS = [col for col in collect_list if 'BMS_Malaga' in col][::-1]
        floors_list_BMS = [c.replace('BMS_Malaga_Climatizacion_', '') for c in collect_list_BMS]

        for i, collection_param in enumerate([col for col in collect_list if 'BMS_Malaga' in col][::-1]):
            run_flow(db, start_date, end_date, temp_data_param, collection_param, floors_list_BMS[i],
                 aggreg_param, cnf.to_zone, rooms_dict, cnf.figure_memory_scale)


main()
