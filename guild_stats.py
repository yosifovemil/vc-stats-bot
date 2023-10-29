from guild_io import GuildIO
import os
from datetime import datetime


class GuildStats:
    def __init__(self, guild_name: str, player_count: int):
        self.guild_name = guild_name
        self.player_count_max = player_count
        self.player_count_current = player_count
        self.guild_io = GuildIO(os.path.join("data", guild_name))

    def add_player(self):
        self.player_count_current += 1
        self.update_max()

    def remove_player(self):
        if self.player_count_current == 0:
            print("Error, tried to remove player but player count is 0")
        else:
            self.player_count_current -= 1

    def minutes_since_update(self):
        last_updated = self.guild_io.fetch_last_timestamp()

        if last_updated is None:
            return 99999
        else:
            now = datetime.now()
            delta = now - last_updated
            return delta.seconds / 60.0

    def write_player_count(self):
        self.guild_io.write(self.player_count_max)
        self.player_count_max = self.player_count_current

    def update_max(self):
        if self.player_count_current > self.player_count_max:
            self.player_count_max = self.player_count_current
