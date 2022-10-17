import json
import pandas as pd
import utils
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from google.oauth2 import service_account
from google.cloud.firestore_v1.field_path import FieldPath
import _thread, weakref, google.cloud.firestore_v1.client as gcc
import times

import logging


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
def get_db_from_firebase_key():
    key_dict = json.loads(st.secrets["firebase_key"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    return firestore.Client(credentials=creds, project="amro-partners")


def _doc_to_pandas_row(doc, field_substring):
    # TODO the sort should (also) be done after using room mapping
    d_vals = dict(sorted(doc.to_dict().items()))
    # iterate over all items in doc and pull the ones containing one of field_substring elements
    d_vals_filtered = dict([(k,[v]) for (k,v) in d_vals.items() if any([i in k for i in field_substring])])
    return pd.DataFrame(d_vals_filtered, index=[doc.id])


# @st.cache(allow_output_mutation=True, ttl=4*3600,
#           show_spinner=False,
#           hash_funcs={
#               weakref.KeyedRef: lambda _: None,
#               _thread.LockType: lambda _: None,
#               gcc.Client: lambda _: None,
#           })
def get_firebase_data(db, collect_name, start_date_utc, end_date_utc, field_substring):
    d = {}
    start_date_utc, end_date_utc = times.convert_datetmie_to_string(start_date_utc, end_date_utc)
    # TODO: Once we have a limited collection pull all data?
    docs = (db.collection(collect_name).stream())


    df_list = []
    for doc in docs:
        if start_date_utc <= times.format_firebase_doc_id_string(doc.id) < end_date_utc:
            df_row = _doc_to_pandas_row(doc, field_substring)
            df_list += [df_row]
    # TODO: remove this utils conversion call once we have a cooked data collection
    return utils.convert_object_cols_to_boolean(pd.concat(df_list))
