import datetime

import discord

from config.values import BOT_ID, CHANNEL_ID_BOT, COLOR_RED, USER_ID_ADMIN
from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)


async def timeout(member: discord.User, **kwargs):
    # if member.id not in [USER_ID_ADMIN, BOT_ID]:
    if member.id not in [BOT_ID]:
        logger.info(f"fn > timeout > start | Member: {member} (id:{member.id})")
        author = kwargs.get("author", "Denis Brogniart")
        reason = kwargs.get("reason", "unknown")
        delta = datetime.timedelta(minutes=kwargs.get("minutes", 10))
        logger.info(
            f"fn > timeout > options | Member: {member} (id:{member.id}) | Requested by: {author} | Timedelta: {delta} | Reason: {reason}"
        )
        await member.timeout(delta, reason=reason)
        embed = discord.Embed(
            title=f":robot: {member} Muted! :moyai:",
            description=f"by **{author}**\nbecause of **{reason}**\nfor **{delta}**",
            color=COLOR_RED,
        )
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
        interaction = kwargs.get("interaction", None)
        if interaction:
            await interaction.followup.send(embed=embed)
        logger.info(f"fn > timeout > OK | Member: {member} (id:{member.id})")
