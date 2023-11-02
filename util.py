import os

from discord import Member, Guild
from typing import Sequence
from discord.ext.commands import Context, Bot
from guild_stats import GuildStats
from logging import Logger


def count_members_in_vc(members: Sequence[Member]):
    player_count = 0
    for member in members:
        if member.voice is not None and member.voice.channel is not None:
            player_count += 1

    return player_count


def get_guild(ctx: Context, guilds: list[GuildStats], logger: Logger):
    channels_whitelist = [int(x) for x in map(str.strip, os.getenv("CHANNELS_WHITELIST").split(","))]
    logger.info(channels_whitelist)
    if ctx.channel.id not in channels_whitelist:
        logger.warning(f"Channel {ctx.channel.name} with id {ctx.channel.id} not in whitelist.")
        return None
    else:
        return get_guild_by_name(ctx.guild.name, guilds, logger)


def get_guild_by_name(guild_name: str, guilds: list[GuildStats], logger: Logger):
    matching_guilds = [g for g in guilds if g.guild_name == guild_name]

    if len(matching_guilds) != 1:
        logger.error(f"Found {len(matching_guilds)} guilds when searching for {guild_name}")
        return None
    else:
        return matching_guilds[0]


def guild_exists(guild: Guild, guilds: list[GuildStats]):
    existing_guilds = [guild_stats for guild_stats in guilds if guild_stats.guild_name == guild.name]

    return len(existing_guilds) > 0
