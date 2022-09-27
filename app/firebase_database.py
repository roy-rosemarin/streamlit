import json
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from google.oauth2 import service_account
import _thread, weakref, google.cloud.firestore_v1.client as gcc
import times


@st.cache(allow_output_mutation=True, ttl=24*3600)
def get_db_from_cert_file(cert_file):
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


@st.cache(allow_output_mutation=True, ttl=24*3600, hash_funcs={dict: lambda _: None})
def get_db_from_textkey():
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    return firestore.Client(credentials=creds, project="amro-partners")


def _doc_to_pandas_row(doc):
    d_vals = dict(sorted(doc.to_dict().items()))
    d_temps = dict([(k,[v]) for (k,v) in d_vals.items() if 'Room_Temp' in k])
    d_states = dict([(k,[v]) for (k,v) in d_vals.items() if 'State' in k])
    return pd.DataFrame(d_temps, index=[doc.id]), pd.DataFrame(d_states, index=[doc.id])


@st.cache(allow_output_mutation=True, ttl=4*3600,
          hash_funcs={
              weakref.KeyedRef: lambda _: None,
              _thread.LockType: lambda _: None,
              gcc.Client: lambda _: None
          })
def get_firebase_data(db, collect_name, start_date, end_date, to_zone):
    start_date_utc, end_date_utc = times.change_ts_time_zone(start_date, end_date, to_zone, 'UTC')
    users_ref = db.collection(collect_name)
    docs = users_ref.stream()

    df_temps_list = []
    df_states_list = []
    for doc in docs:
        if start_date_utc <= doc.id[:19].replace('T', ' ') < end_date_utc:
            df_temps_row, df_states_row = _doc_to_pandas_row(doc)
            df_temps_list += [df_temps_row]
            df_states_list += [df_states_row]

    return df_temps_list, df_states_list
