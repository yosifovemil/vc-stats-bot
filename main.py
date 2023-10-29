# Import the required modules
from typing import Sequence
from datetime import datetime
import discord
import os

from discord import Member
from discord.ext import commands, tasks
from dotenv import load_dotenv
from guild_stats import GuildStats

# Create a Discord client instance and set the command prefix
intents = discord.Intents.none()
intents.members = True
intents.guilds = True
intents.voice_states = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

guild_stats: list[GuildStats] = []


# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    for guild in bot.guilds:
        player_count = count_members_in_vc(guild.members)
        guild_stat_entry = GuildStats(guild_name=guild.name, player_count=player_count)
        guild_stats.append(guild_stat_entry)
        print(f"Added guild {guild_stat_entry.guild_name}")

    record_player_count.start()


def count_members_in_vc(members: Sequence[Member]):
    player_count = 0
    for member in members:
        if member.voice is not None and member.voice.channel is not None:
            player_count += 1

    return player_count


@bot.event
async def on_voice_state_update(member: Member, before, after):
    entries = [entry for entry in guild_stats if entry.guild_name == member.guild.name]

    if len(entries) > 1:
        print(f"Member {member.name} has more than 1 guilds")
    elif len(entries) == 0:
        print(f"Member {member.name} has 0 guilds")
    else:
        if (before.channel is None) and (after.channel is not None):
            entries[0].add_player()
        elif (before.channel is not None) and (after.channel is None):
            entries[0].remove_player()


@tasks.loop(minutes=30)
async def record_player_count():
    timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    for guild_entry in guild_stats:
        player_count = guild_entry.get_player_count_max()

        f = open(os.path.join("data", guild_entry.guild_name), 'a')
        f.write(f"{timestamp},{player_count}\n")
        f.close()


# Retrieve token from the .env file
load_dotenv()
bot.run(os.getenv('TOKEN'))
