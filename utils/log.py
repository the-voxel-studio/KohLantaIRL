import discord

from utils.bot import bot
from config.values import CHANNEL_ID_BOT, COLOR_GREEN, COLOR_ORANGE, COLOR_RED, CHANNEL_ID_BOT_LOGS #COULEURS OBLIGATOIRES (utilisation de la fonction eval)
from utils.logging import get_logger

import os
from pathlib import Path

logger = get_logger(__name__)
# DIRNAME = os.path.dirname(__file__)
DIRNAME = Path(__file__).parent.parent

async def send_log(title: str, *args, **kwargs):
    bot_channel = bot.get_channel(CHANNEL_ID_BOT)
    if len(args) != 0:
        color = kwargs.get("color", "ORANGE").upper()
        embed=discord.Embed(title=f":robot: {title} :moyai:", color=eval("COLOR_"+color))
        embed.description = "\n".join(args)
        await bot_channel.send(embed=embed)
    else:
        await bot_channel.send(title)

async def send_logs_file():
    logger.info(f"fn > send_logs_file > start")
    bot_logs_channel = bot.get_channel(CHANNEL_ID_BOT_LOGS)
    if os.name == "nt":
        file = discord.File(f"{DIRNAME}\\logs\\bot.log")
    else:
        file = discord.File(f"{DIRNAME}/logs/bot.log")
    
    await bot_logs_channel.send(file=file)
    logger.info(f"fn > send_logs_file > OK")