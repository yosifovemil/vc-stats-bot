from typing import Sequence
import discord
import os
import logging
from discord import Member, Guild
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

import util
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
    guild = util.get_guild(ctx, guilds, logger)

    if guild is not None:
        data = guild.guild_io.read_file()
        data = data[data['Player count'] > 0]
        data = data.to_markdown(index=False)

        data = "```" + data + "```"

        await ctx.send(data)


@bot.command()
async def plot_activity(ctx: Context):
    guild = util.get_guild(ctx, guilds, logger)

    if guild is not None:
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
        if not util.guild_exists(discord_guild, guilds):
            player_count = util.count_members_in_vc(discord_guild.members)
            guild_stats = GuildStats(guild_name=discord_guild.name, player_count=player_count)

            guilds.append(guild_stats)
            logger.info(f"Added guild {guild_stats.guild_name}")

    automatic_activity_plot.start()


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


@tasks.loop(hours=24)
async def automatic_activity_plot():
    logger.info("Posting daily activity")
    channel_id = int(os.getenv("AUTOMATIC_CHANNEL_ID"))
    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    if channel is None:
        logger.error(f"Could not find channel with ID {channel_id}")
    else:
        filename = os.path.join("images", str(uuid.uuid4()) + ".png")
        guild = util.get_guild_by_name(channel.guild.name, guilds, logger)
        if guild is None:
            logger.error(f"Could not find guild with name {channel.guild.name}")
        else:
            plotter.plot(guild.guild_io, filename)

            with open(filename, 'rb') as f:
                plot = discord.File(f)
                await channel.send(file=plot)

            f.close()
            os.remove(filename)


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv('TOKEN'))
