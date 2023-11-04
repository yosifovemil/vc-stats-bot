import pandas as pd
from pandas import Timestamp

from guild_io import GuildIO
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def plot(guild_io: GuildIO, tempfile: str):
    data = load_data(guild_io)
    data = interpolate_readings(data)
    data = fill_missing_data(data)

    data['Player count'] = data['Player count'].round(1)

    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    data_wide = data.pivot_table(index='hour', columns='day', values='Player count', aggfunc=lambda x: x)
    data_wide = data_wide.set_axis(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], axis=1)

    colors = ["#E0E0E0", "#FFFD9D", "#fefd63", "#FEFB01", "#CEFB02", "#87FA00", "#3AF901", "#00ED01"]
    color_palette = sns.color_palette(colors)

    sns.heatmap(data_wide, ax=ax, linewidths=1.0, annot=True, cmap=color_palette, vmin=0, vmax=4)
    plt.savefig(tempfile, dpi=200)


def load_data(guild_io: GuildIO):
    data = guild_io.read_file()
    data.index = data['Date']

    return data


def interpolate_readings(data):
    start = data['Date'].min()
    end = pd.Timestamp.now()
    dates = pd.DataFrame(pd.date_range(start, end, freq="S"), columns=['Date'])
    dates.index = dates['Date']

    data = dates.join(data, lsuffix="_left", rsuffix="_right", how='outer')['Player count']
    data.ffill(axis=0, inplace=True)
    data = pd.DataFrame(data, columns=['Player count'])

    return data


def fill_missing_data(data):
    data['hour'] = pd.to_datetime(data.index).hour
    data['day'] = pd.to_datetime(data.index).day_of_week
    data = data.groupby(['day', 'hour'], as_index=False).mean()
    data.set_index(['day', 'hour'], inplace=True)

    days_df = pd.DataFrame(np.arange(0, 7), columns=['day'])
    hours_df = pd.DataFrame(np.arange(0, 24), columns=['hour'])
    empty_df = days_df.merge(hours_df, how='cross')
    empty_df.set_index(['day', 'hour'], inplace=True)

    data = data.join(empty_df, how='outer')
    data.fillna(0, inplace=True)
    data.reset_index(inplace=True)

    return data


def seconds_to_zero(d: Timestamp):
    return d.replace(second=0)


def get_day_of_week(day: int):
    return days_of_week[day]
