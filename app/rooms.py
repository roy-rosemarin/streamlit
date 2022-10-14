import os
import re
import streamlit as st
import pandas as pd


@st.cache(allow_output_mutation=True, ttl=24*3600)
def read_room_file(rooms_mapping_file):
    path = os.path.dirname(__file__)
    return pd.read_csv(os.path.join(path, rooms_mapping_file), encoding='latin-1')


@st.cache(allow_output_mutation=True, ttl=24*3600)
def get_floor_to_rooms_dict(rooms_mapping_file):
    rooms_df = read_room_file(rooms_mapping_file)
    rooms_df = rooms_df[['ROOM', 'Title']].groupby('Title')['ROOM'].apply(list)
    return rooms_df.to_dict()


@st.cache(allow_output_mutation=True, ttl=24*3600)
def get_code_to_room_dict(rooms_mapping_file):
    rooms_df = read_room_file(rooms_mapping_file)
    rooms_df = (rooms_df[['Gateway', 'ROOM', 'BACnet reading number', 'Title']]
                .set_index(['Gateway', 'BACnet reading number']))
    return rooms_df.to_dict(orient='index')


def map_rooms_names(df, rooms_dict, gateway_room_pattern):
    new_columns = []
    new_titles = []
    for room_id in df.columns:
        match = re.search(gateway_room_pattern, room_id)
        if match:
            val = (int(match.group(1)), int(match.group(2)))
            key = rooms_dict[val]
            if key:
                new_columns += [key['ROOM']]
                new_titles += [key['Title']]
            else:
                new_columns += [room_id]
                new_titles += ['']
        else:
            new_columns += [room_id]
            new_titles += ['']

    df.columns = pd.MultiIndex.from_arrays([new_titles, new_columns])  # new_columns
    return df
