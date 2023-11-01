from guild_io import GuildIO
import os


class GuildStats:
    def __init__(self, guild_name: str, player_count: int):
        self.guild_name = guild_name
        self.player_count = player_count
        self.guild_io = GuildIO(os.path.join("data", guild_name))
        self.write_player_count()

    def add_player(self):
        self.player_count += 1
        self.write_player_count()

    def remove_player(self):
        if self.player_count == 0:
            print("Error, tried to remove player but player count is 0")
        else:
            self.player_count -= 1
            self.write_player_count()

    def write_player_count(self):
        self.guild_io.write(self.player_count)
