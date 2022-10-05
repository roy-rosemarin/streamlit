import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import times


def set_date_vars(df, group_by, to_zone=None):
    datetimes = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")
    if to_zone != None:
        datetimes = times.change_pd_time_zone(datetimes, 'UTC', to_zone)

    if group_by == 'Date':
        df['Date'] = datetimes.date
    elif group_by == "Hour of Day":
        df['Hour of Day'] = datetimes.hour

    return df


def plot_heatmap(df, group_by, plot_parms, title, xlabel, ylabel, to_zone, scale):
    df = times.set_date_vars(df, group_by, to_zone=to_zone)
    df_agg = df.groupby(by=[group_by]).mean()

    fmt, vmin, vmax = plot_parms
    fig = plt.figure(figsize=(scale*24, scale*len(df_agg.columns)))
    sns.set(font_scale=scale*2)

    sns.heatmap(df_agg.T.sort_index(), annot=True, annot_kws={"fontsize": scale*16, "weight": "bold"},
                fmt=fmt, linewidths=.5,
                cmap=sns.color_palette("coolwarm", as_cmap=True),
                vmin=vmin, vmax=vmax, cbar=False)

    labels_fontsize = scale * 30
    #plt.title(title, fontsize=labels_fontsize) # title with fontsize 20
    plt.xlabel(xlabel, fontsize=labels_fontsize) # x-axis label with fontsize 15
    plt.ylabel(ylabel, fontsize=labels_fontsize) # y-axis label with fontsize 15
    return fig