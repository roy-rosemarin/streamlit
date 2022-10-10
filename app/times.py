
def convert_datetmie_to_string(start_date_utc, end_date_utc):
    return start_date_utc.strftime('%Y-%m-%d %H:%M:%S'), end_date_utc.strftime('%Y-%m-%d %H:%M:%S')


def change_pd_time_zone(datetime_col, source_tz, destin_tz):
    return datetime_col.tz_localize(source_tz).tz_convert(destin_tz)


def format_firebase_doc_id_string(doc_id):
    return doc_id[:19].replace('T', ' ')
