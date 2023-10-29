from datetime import datetime
import settings
import os


class GuildIO:
    def __init__(self, file_name):
        self.file_name = file_name  #
        if not os.path.exists(self.file_name):
            self.create_file()

    def fetch_last_timestamp(self):
        f = open(self.file_name, 'r')
        lines = f.readlines()
        f.close()

        if len(lines) > 0:
            last_line = lines[-1]
            return datetime.strptime(last_line.split(",")[0], settings.TIME_FORMAT)
        else:
            return None

    def write(self, player_count):
        f = open(self.file_name, 'a')
        timestamp = datetime.now().strftime(settings.TIME_FORMAT)
        f.write(f"{timestamp},{player_count}\n")
        f.close()

    def create_file(self):
        f = open(self.file_name, 'w')
        f.close()
