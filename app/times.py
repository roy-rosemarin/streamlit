from dateutil import tz
import pandas as pd


def change_ts_time_zone(start_date, end_date, source_tz, destin_tz):
    start_date_utc = start_date.replace(tzinfo=tz.gettz(source_tz)).astimezone(tz.gettz(destin_tz)).strftime('%Y-%m-%d %H:%M:%S')
    end_date_utc = end_date.replace(tzinfo=tz.gettz(source_tz)).astimezone(tz.gettz(destin_tz)).strftime('%Y-%m-%d %H:%M:%S')
    return start_date_utc, end_date_utc


def change_pd_time_zone(timestamp, source_tz, destin_tz):
    return timestamp.tz_localize(source_tz).tz_convert(destin_tz)


def set_date_vars(df, group_by, to_zone=None):
    datetimes = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
    if to_zone != None:
        datetimes = change_pd_time_zone(datetimes, 'UTC', to_zone)

    if group_by == 'Date':
        df['Date'] = datetimes.date
    elif group_by == "Hour of Day":
        df['Hour of Day'] = datetimes.hour

    return df
