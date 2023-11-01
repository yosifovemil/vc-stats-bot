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
import plotter
import uuid

# Logging setup
logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger("VC stats bot")
logger.setLevel(logging.NOTSET)
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
    logger.info(f"Activity requested from channel {ctx.channel.name}")

    if ctx.channel.name.find("captains-quarters") == -1:
        logger.info("Channel is not captains-quarters")
        return
    elif len(matching_guilds) != 1:
        logger.error(f"Found {len(matching_guilds)} guilds when searching for {ctx.guild.name}")
    else:
        logger.info("Fetching player count")
        guild = matching_guilds[0]
        data = guild.guild_io.read_file()
        data = data[data['Player count'] > 0]
        data = data.to_markdown(index=False)

        data = "```" + data + "```"

        await ctx.send(data)


@bot.command()
async def plot_activity(ctx: Context):
    matching_guilds = [g for g in guilds if g.guild_name == ctx.guild.name]
    logger.info(f"Activity plot requested from channel {ctx.channel.name}")

    if ctx.channel.name.find("captains-quarters") == -1:
        logger.info("Channel is not captains-quarters")
        return
    elif len(matching_guilds) != 1:
        logger.error(f"Found {len(matching_guilds)} guilds when searching for {ctx.guild.name}")
    else:
        guild = matching_guilds[0]
        filename = os.path.join("images", str(uuid.uuid4()) + ".png")
        plotter.plot(guild.guild_io, filename)
        with open(filename, 'rb') as f:
            plot = discord.File(f)
            await ctx.send(file=plot)

        f.close()
        os.remove(filename)


@bot.event
async def on_ready():
    for discord_guild in bot.guilds:
        if not guild_exists(discord_guild):
            player_count = count_members_in_vc(discord_guild.members)
            guild_stats = GuildStats(guild_name=discord_guild.name, player_count=player_count)

            guilds.append(guild_stats)
            logger.info(f"Added guild {guild_stats.guild_name}")


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


# Retrieve token from the .env file
load_dotenv()
bot.run(os.getenv('TOKEN'))
