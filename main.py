from typing import Sequence
import discord
import os
import logging
from discord import Member, Guild
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
from guild_stats import GuildStats
import settings

# Logging setup
logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger("VC stats bot")
formatter = logging.Formatter(settings.LOGGING_FORMAT, settings.LOGGING_TIME_FORMAT)
ch = logging.StreamHandler()
ch.setLevel(logging.NOTSET)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Create a Discord client instance and set the command prefix
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)

# Keep track of all discord guilds that have added the bot
guilds: list[GuildStats] = []


@bot.command()
async def activity(ctx: Context):
    matching_guilds = [g for g in guilds if g.guild_name == ctx.guild.name]

    if len(matching_guilds) != 1:
        logger.error(f"Found {len(matching_guilds)} guilds when searching for {ctx.guild.name}")
    else:
        guild = matching_guilds[0]
        data = guild.guild_io.read_file()
        data = data[data['Player count'] > 0]
        data = data.to_markdown(index=False)

        data = "```" + data + "```"

        await ctx.send(data)


@bot.event
async def on_ready():
    for discord_guild in bot.guilds:
        if not guild_exists(discord_guild):
            player_count = count_members_in_vc(discord_guild.members)
            guild_stats = GuildStats(guild_name=discord_guild.name, player_count=player_count)

            guilds.append(guild_stats)
            logger.info(f"Added guild {guild_stats.guild_name}")

    update.start()


def guild_exists(guild: Guild):
    existing_guilds = [guild_stats for guild_stats in guilds if guild_stats.guild_name == guild.name]

    return len(existing_guilds) > 0


def count_members_in_vc(members: Sequence[Member]):
    player_count = 0
    for member in members:
        if member.voice is not None and member.voice.channel is not None:
            player_count += 1

    return player_count


@bot.event
async def on_voice_state_update(member: Member, before, after):
    matching_guilds = [entry for entry in guilds if entry.guild_name == member.guild.name]

    if len(matching_guilds) > 1:
        logger.error(f"Member {member.name} has more than 1 guilds")
    elif len(matching_guilds) == 0:
        logger.error(f"Member {member.name} has 0 guilds")
    else:
        if (before.channel is None) and (after.channel is not None):
            logger.info(f"Adding player to {member.guild.name}")
            matching_guilds[0].add_player()
        elif (before.channel is not None) and (after.channel is None):
            logger.info(f"Removing player from {member.guild.name}")
            matching_guilds[0].remove_player()


@tasks.loop(minutes=1)
async def update():
    for guild_entry in guilds:
        if guild_entry.minutes_since_update() >= settings.UPDATE_PERIOD:
            guild_entry.write_player_count()


# Retrieve token from the .env file
load_dotenv()
bot.run(os.getenv('TOKEN'))
