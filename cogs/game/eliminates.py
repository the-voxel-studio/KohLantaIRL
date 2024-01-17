import discord
from discord import app_commands
from discord.ext import commands

from utils.logging import get_logger

logger = get_logger(__name__)


class EliminatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO /message command for eliminates players
    # - one msg authorized every day


async def setup(bot):
    await bot.add_cog(EliminatesCog(bot))
    logger.info(f"Loaded !")
