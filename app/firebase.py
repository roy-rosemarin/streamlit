import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st
import pickle
import json
from google.oauth2 import service_account

pd.options.mode.chained_assignment = None  # default='warn'


def get_db_from_firebase_key():
    key_dict = json.loads(st.secrets["firebase_key"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    firebase_admin.initialize_app(creds, {'storageBucket': cnf.storage_bucket})
    return firestore.Client(credentials=creds, project="amro-partners")


def get_db_from_cert_file(cert_file, storage_bucket):
    # Use a service account
    try:
        app = firebase_admin.get_app()
    except ValueError as e:
        cred = credentials.Certificate(cert_file)
        try:
            firebase_admin.initialize_app(cred, {'storageBucket': storage_bucket})
        except ValueError as e:
            pass

    return firestore.client()


@st.experimental_memo(show_spinner=False)
def read_and_unpickle(file_name, bucket_name=None):
    return pickle.loads(storage.bucket(bucket_name).blob(file_name).download_as_string(timeout=300))


@st.experimental_memo(show_spinner=False)
def read_and_unpickle_and_concat(file_name, bucket_name=None):
    return pickle.loads(storage.bucket(bucket_name).blob(file_name).download_as_string(timeout=300))

