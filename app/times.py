from dateutil import tz


def change_ts_time_zone(start_date, end_date, source_tz, destin_tz):
    start_date_utc = start_date.replace(tzinfo=tz.gettz(source_tz)).astimezone(tz.gettz(destin_tz)).strftime('%Y-%m-%d %H:%M:%S')
    end_date_utc = end_date.replace(tzinfo=tz.gettz(source_tz)).astimezone(tz.gettz(destin_tz)).strftime('%Y-%m-%d %H:%M:%S')
    return start_date_utc, end_date_utc


def change_pd_time_zone(timestamp, source_tz, destin_tz):
    return timestamp.tz_localize(source_tz).tz_convert(destin_tz)
