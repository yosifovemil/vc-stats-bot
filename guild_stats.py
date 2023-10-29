class GuildStats:
    def __init__(self, guild_name: str, player_count: int):
        self.guild_name = guild_name
        self.player_count_max = player_count
        self.player_count_current = player_count

    def add_player(self):
        self.player_count_current += 1
        self.update_max()

    def remove_player(self):
        if self.player_count_current == 0:
            print("Error, tried to remove player but player count is 0")
        else:
            self.player_count_current -= 1

    def get_player_count_max(self):
        player_count_max = self.player_count_max
        self.reset_counter(self.player_count_current)
        return player_count_max

    def reset_counter(self, player_count: int):
        self.player_count_current = player_count
        self.player_count_max = player_count

    def update_max(self):
        if self.player_count_current > self.player_count_max:
            self.player_count_max = self.player_count_current
