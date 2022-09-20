import os
import re
import json
import weakref, _thread
from datetime import datetime, timedelta
from dateutil import tz
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.oauth2 import service_account
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import streamlit as st
import PIL.Image

matplotlib.use('Agg')
PIL.Image.MAX_IMAGE_PIXELS = 300000000
@st.cache(ttl=1*3600)


def get_db(cert_file):
    # Use a service account
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(cert_file)
        try:
            firebase_admin.initialize_app(cred)
        except ValueError as e:
            pass

    return firestore.client()


def doc_to_pandas_row(doc):
    d_vals = dict(sorted(doc.to_dict().items()))
    d_temps = dict([(k,[v]) for (k,v) in d_vals.items() if 'Room_Temp' in k])
    d_states = dict([(k,[v]) for (k,v) in d_vals.items() if 'State' in k])
    return pd.DataFrame(d_temps, index=[doc.id]), pd.DataFrame(d_states, index=[doc.id])


def convert_object_cols_to_boolean(df):
    df[df.columns[df.dtypes == 'object']] = (df[df.columns[df.dtypes == 'object']] == True)
    return df


def fix_date_vars(df, group_by, to_zone=None):
    datetimes = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
    if to_zone != None:
        datetimes = datetimes.tz_localize('UTC').tz_convert(to_zone)

    if group_by == 'Date':
        df['Date'] = datetimes.date
    elif group_by == "Hour of Day":
        df['Hour of Day'] = datetimes.hour

    return df


@st.cache(allow_output_mutation=True,
          hash_funcs={weakref.KeyedRef: lambda _: None, _thread.LockType: lambda _: None})
def get_firebase_data(collect_name, start_date, end_date, to_zone):
    start_date_utc = start_date.replace(tzinfo=tz.gettz(to_zone)).astimezone(tz.gettz('UTC')).strftime('%Y-%m-%d %H:%M:%S')
    end_date_utc = end_date.replace(tzinfo=tz.gettz(to_zone)).astimezone(tz.gettz('UTC')).strftime('%Y-%m-%d %H:%M:%S')

    users_ref = db.collection(collect_name)
    docs = users_ref.stream()

    df_temps_list = []
    df_states_list = []
    for doc in docs:
        if start_date_utc <= doc.id[:10] <= end_date_utc:
            df_temps_row, df_states_row = doc_to_pandas_row(doc)
            df_temps_list += [df_temps_row]
            df_states_list += [df_states_row]

    df_temps = pd.concat(df_temps_list)
    df_states = pd.concat(df_states_list)

    return df_temps, df_states



@st.cache(hash_funcs={plt.figure: lambda _: None}, allow_output_mutation=True, suppress_st_warning=True)
def plot_heatmap(df, group_by, plot_parms, title, xlabel, ylabel, to_zone, scale):
    df = fix_date_vars(df, group_by, to_zone=to_zone)
    df_agg = df.groupby(by=[group_by]).mean()

    fmt, vmin, vmax = plot_parms
    fig = plt.figure(figsize=(scale*24, scale*len(df_agg.columns)))
    sns.set(font_scale=scale*2)

    sns.heatmap(df_agg.T.sort_index(), annot=True,  annot_kws={"fontsize": scale*20, "weight": "bold"},
                fmt=fmt, linewidths=.5,
                cmap=sns.color_palette("coolwarm", as_cmap=True),
                vmin=vmin, vmax=vmax, cbar=False)

    labels_fontsize = scale * 30
    plt.title(title, fontsize=labels_fontsize) # title with fontsize 20
    plt.xlabel(xlabel, fontsize=labels_fontsize) # x-axis label with fontsize 15
    plt.ylabel(ylabel, fontsize=labels_fontsize) # y-axis label with fontsize 15
    return fig


def set_general_settings(start_date, end_date, temp_data_list, floors_list, aggregation_list):
    # if st.button('Balloons?'):
    #     st.balloons()

    st.header('MALAGA AIR CONDITIONING HEATMAPS')
    st.caption(f'Version 1.0, release data: 16/09/2022')
    st.caption(f'Data pulled over the last 7 days between dates: {start_date} - {end_date}')

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


def map_rooms_names(df, rooms_dict):
    new_columns = []
    for room_id in df.columns:
        match = re.search(r'VRV([\d]+).[\w.-]+_([\d]+).', room_id)
        if match:
            new_columns += [rooms_dict[(int(match.group(1)), int(match.group(2)))]]
        else:
            new_columns += [room_id]

    df.columns = new_columns
    return df


@st.cache(allow_output_mutation=True)
def get_rooms_dict(rooms_mapping_file):
    #rooms_df = pd.read_csv(os.path.join(os.path.realpath('./'), rooms_mapping_file), encoding='latin-1')
    path = os.path.dirname(__file__)
    rooms_df = pd.read_csv(os.path.join(path, rooms_mapping_file), encoding='latin-1')

    rooms_df = rooms_df[['Gateway', 'ROOM', 'BACnet reading number']].set_index(['Gateway', 'BACnet reading number'])
    return rooms_df.to_dict()['ROOM']


def main(start_date, end_date, temp_data_param, collection_param, floor_param,
         aggreg_param, to_zone, rooms_dict, figure_memory_scale):
    df_temps, df_states = get_firebase_data(collection_param,
                                            start_date,
                                            end_date,
                                            to_zone)

    df_states = convert_object_cols_to_boolean(df_states)

    # df_temp_data is pandas dataframes with the pulled data.
    if temp_data_param == "Avg. degrees (°C)":
        df_temp_data = df_temps
        fmt, vmin, vmax = '.1f', 15, 40
    elif temp_data_param == '"On" frequency (%)':
        df_temp_data = df_states
        fmt, vmin, vmax = '0.0%', 0, 1

    if temp_data_param != "Select A/C data":
        df_temp_data = map_rooms_names(df_temp_data, rooms_dict)

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



# Config
figure_memory_scale = 0.2 # scaling the original seaborn in order to reduce memory usage

to_zone = 'Europe/Madrid' # local zone
cert_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.json" # certification file for firebase authentication
rooms_mapping_file = "rooms_codes_malaga.csv" # file cotaining mapping of API rooms' codes to rooms' names

temp_data_list = ("Select A/C data",
                    "Avg. degrees (°C)",
                    '"On" frequency (%)')

collect_list = ["Select floor",
                "All",
                "BMS_Malaga_Climatizacion_Planta_S",
                "BMS_Malaga_Climatizacion_Planta_B",
                "BMS_Malaga_Climatizacion_Planta_1",
                "BMS_Malaga_Climatizacion_Planta_2",
                "BMS_Malaga_Climatizacion_Planta_3",
                "BMS_Malaga_Climatizacion_Planta_4"]

aggregation_list = ("Select aggregation by",
                    "Date",
                    "Hour of Day")


floors_list = [c.replace('BMS_Malaga_Climatizacion_', '') for c in collect_list]
rooms_dict = get_rooms_dict(rooms_mapping_file)


#cert_file_path = os.path.join(os.path.realpath('../'), cert_file)
#db = get_db(cert_file_path)
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="amro-partners")

start_date = (datetime.today() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
end_date = (datetime.today() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

collection_param, temp_data_param, floor_param, aggreg_param = \
    set_general_settings(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                         temp_data_list, tuple(floors_list), aggregation_list)

if floor_param not in ('Select floor', "All"):
    main(start_date, end_date, temp_data_param, collection_param, floor_param,
         aggreg_param, to_zone, rooms_dict, figure_memory_scale)
elif floor_param == "All":
    collect_list_BMS = [col for col in collect_list if 'BMS_Malaga' in col][::-1]
    floors_list_BMS = [c.replace('BMS_Malaga_Climatizacion_', '') for c in collect_list_BMS]

    for i, collection_param in enumerate([col for col in collect_list if 'BMS_Malaga' in col][::-1]):
        main(start_date, end_date, temp_data_param, collection_param, floors_list_BMS[i],
             aggreg_param, to_zone, rooms_dict, figure_memory_scale)


