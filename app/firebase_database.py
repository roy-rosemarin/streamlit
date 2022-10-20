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

pd.options.mode.chained_assignment = None  # default='warn'


@st.cache(allow_output_mutation=True, ttl=times.seconds_until_midnight())
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


@st.cache(allow_output_mutation=True, ttl=times.seconds_until_midnight(), hash_funcs={dict: lambda _: None})
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


@st.cache(allow_output_mutation=True, ttl=times.seconds_until_midnight(),
          show_spinner=False,
          hash_funcs={
              weakref.KeyedRef: lambda _: None,
              _thread.LockType: lambda _: None,
              gcc.Client: lambda _: None,
          })
def get_firebase_data(db, collect_name, start_date_utc, end_date_utc, field_substring):
    def _doc_to_lst(collection, doc):
        nonlocal df_list, field_substring
        df_list += [_doc_to_pandas_row(doc, field_substring)]

    start_date_utc, end_date_utc = times.convert_datetmie_to_string(start_date_utc, end_date_utc)
    docs = db.collection(collect_name).stream()

    df_list = []
    collection = (db.collection(collect_name)
                  .where('datetime', '>=', start_date_utc)
                  .where('datetime', '<', end_date_utc))
    stream_collection_loop(collection, _doc_to_lst)
    # TODO: remove this utils conversion call once we have a cooked data collection
    return utils.convert_object_cols_to_boolean(pd.concat(df_list))


def stream_collection_loop(collection, my_func, **kwargs):
    '''
    streams efficiently over a collection and implement my_func function
    collection: The collection to stream over, e.g. db.collection('test_weather_Seville')
    my_func: the function name to run. The first two parameters of this function has to be: collection, doc
    **kwargs: additional potential arguments values to be used by my_func
    '''
    cursor = None
    limit = 1000

    while True:
        docs = []  # Very important. This frees the memory incurred in the recursion algorithm.

        if cursor:
            docs = [snapshot for snapshot in
                    collection.limit(limit).start_after(cursor).stream()]
        else:
            docs = [snapshot for snapshot in collection.limit(limit).stream()]

        for doc in docs:
            my_func(collection, doc, **kwargs)

        if len(docs) == limit:
            cursor = docs[limit - 1]
            continue

        break