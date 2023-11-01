from datetime import datetime
import settings
import os
import pandas as pd


class GuildIO:
    def __init__(self, file_name):
        self.file_name = file_name  #
        if not os.path.exists(self.file_name):
            self.create_file()

    def write(self, player_count):
        f = open(self.file_name, 'a')
        timestamp = datetime.now().strftime(settings.TIME_FORMAT)
        f.write(f"{timestamp},{player_count}\n")
        f.close()

    def create_file(self):
        f = open(self.file_name, 'w')
        f.close()

    def read_file(self):
        f = open(self.file_name, 'r')
        lines = f.readlines()
        f.close()

        dates = []
        counts = []

        for line in lines:
            vals = line.split(",")
            date = datetime.strptime(vals[0], settings.TIME_FORMAT)
            player_count = int(vals[1].strip())

            dates.append(date)
            counts.append(player_count)

        return pd.DataFrame(list(zip(dates, counts)), columns=['Date', 'Player count'])
