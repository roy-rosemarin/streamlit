from datetime import datetime
from pytz import timezone
import streamlit as st


def utc_now():
    return datetime(2022, 11, 15, 0, 0)  ################  TODO: change back to datetime.utcnow()


@st.experimental_singleton
def last_cache_date():
    return utc_now().strftime('%Y-%m-%d')


def localise_time_now(tz):
    return timezone('UTC').localize(utc_now()).astimezone(timezone(tz))


def convert_datetmie_to_string(start_date_utc, end_date_utc):
    return start_date_utc.strftime('%Y-%m-%dT%H:%M:%S'), end_date_utc.strftime('%Y-%m-%dT%H:%M:%S')


def change_pd_time_zone(datetime_col, source_tz, destin_tz):
    return datetime_col.tz_localize(source_tz).tz_convert(destin_tz)


def format_firebase_doc_id_string(doc_id):
    return doc_id[:19].replace('T', ' ')


def seconds_until_midnight(dt=None):
    if dt is None:
        dt = utc_now()
    return ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)


def milliseconds_until_midnight(dt=None):
    return 1000 * seconds_until_midnight(dt)


def log_time(times, key):
    now = utc_now()
    if times.get('last'):
        times[key] = (now - times['last']).total_seconds()
    else:
        times[key] = now

    times['last'] = now
    return key, times[key]
