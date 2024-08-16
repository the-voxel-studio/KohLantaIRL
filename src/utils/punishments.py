import datetime

import discord

from config.values import BOT_ID, CHANNEL_ID_BOT, COLOR_RED
from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)


async def timeout(member: discord.User, **kwargs):
    """Timeout a member."""

    if member.id not in [BOT_ID]:
        logger.info(f'fn > timeout > start | Member: {member} (id:{member.id})')
        author = kwargs.get('author', 'Denis Brogniart')
        reason = kwargs.get('reason', 'unknown')
        interaction = kwargs.get('interaction', None)
        delta = datetime.timedelta(minutes=kwargs.get('minutes', 10))
        logger.info(
            f'fn > timeout > options | Member: {member} (id:{member.id}) | Requested by: {author} | Timedelta: {delta} | Reason: {reason}'
        )
        try:
            await member.timeout(delta, reason=reason)
            embed = discord.Embed(
                title=f':robot: {member} Muted! :moyai:',
                description=f'by **{author}**\nbecause of **{reason}**\nfor **{delta}**',
                color=COLOR_RED,
            )
            await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
            if interaction:
                await interaction.followup.send(embed=embed)
            logger.info(f'fn > timeout > OK | Member: {member} (id:{member.id})')
        except discord.errors.Forbidden:
            if interaction:
                embed = discord.Embed(
                    title=f':robot: impossible to mute {member} :moyai:',
                    description=f'by **{author}**\nbecause of **{reason}**\nfor **{delta}**\nerror `missing permission of the bot`',
                    color=COLOR_RED,
                )
                await interaction.followup.send(embed=embed)
            logger.error(f'fn > timeout > Missing Permission | Member: {member} (id:{member.id})')
