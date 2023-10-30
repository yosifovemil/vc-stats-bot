from guild_io import GuildIO
from datetime import datetime
import numpy as np
import matplotlib.colors as mc
import matplotlib.pyplot as plt


def plot(guild_io: GuildIO, days: int):
    current_day = datetime.now().day

    data = guild_io.read_file()
    data['hour'] = data['Date'].dt.hour
    data['day'] = data['Date'].dt.day - current_day

    data = data[data['day'] >= (0 - days)]

    hour = data['hour']
    day = data['day']
    count = data['Player count'].values.reshape(min(48, len(data)), len(day.unique()), order="F")

    xgrid = np.arange(day.min(), 1)

    # Hours start at 0, length 2
    ygrid = np.arange(max(hour) + 1)

    fig, ax = plt.subplots()
    ax.pcolormesh(xgrid, ygrid, temp)
    ax.set_frame_on(False)  # remove all spines




import plotter
from guild_io import GuildIO

plotter.plot(GuildIO("data/Storm 0f Ale's server"),  1)