from datetime import datetime


def convert_datetmie_to_string(start_date_utc, end_date_utc):
    return start_date_utc.strftime('%Y-%m-%d %H:%M:%S'), end_date_utc.strftime('%Y-%m-%d %H:%M:%S')


def change_pd_time_zone(datetime_col, source_tz, destin_tz):
    return datetime_col.tz_localize(source_tz).tz_convert(destin_tz)


def format_firebase_doc_id_string(doc_id):
    return doc_id[:19].replace('T', ' ')


def seconds_until_midnight(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)


def milliseconds_until_midnight(dt=None):
    return 1000 * seconds_until_midnight(dt)
