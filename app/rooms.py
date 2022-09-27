import os
import re
import streamlit as st
import pandas as pd


@st.cache(allow_output_mutation=True, ttl=24*3600)
def get_rooms_dict(rooms_mapping_file):
    path = os.path.dirname(__file__)
    rooms_df = pd.read_csv(os.path.join(path, rooms_mapping_file), encoding='latin-1')

    rooms_df = rooms_df[['Gateway', 'ROOM', 'BACnet reading number']].set_index(['Gateway', 'BACnet reading number'])
    return rooms_df.to_dict()['ROOM']


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
