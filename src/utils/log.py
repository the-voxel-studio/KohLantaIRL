import os
from pathlib import Path

import discord

from config.values import (
    CHANNEL_ID_BOT,
    CHANNEL_ID_BOT_LOGS,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_RED,
)
from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)
COLOR_GREEN, COLOR_ORANGE, COLOR_RED  # COULEURS OBLIGATOIRES (utilisation de la fonction eval)
DIRNAME = Path(__file__).parent.parent.parent


async def send_log(title: str, *args, **kwargs):
    bot_channel = bot.get_channel(CHANNEL_ID_BOT)
    if len(args) != 0:
        color = kwargs.get('color', 'ORANGE').upper()
        embed = discord.Embed(
            title=f':robot: {title} :moyai:', color=eval('COLOR_' + color)
        )
        embed.description = '\n'.join(args)
        await bot_channel.send(embed=embed)
    else:
        await bot_channel.send(title)


async def send_logs_file():
    logger.info('fn > send_logs_file > start')
    bot_logs_channel = bot.get_channel(CHANNEL_ID_BOT_LOGS)
    if os.name == 'nt':
        file = discord.File(f'{DIRNAME}\\logs\\bot.log')
    else:
        file = discord.File(f'{DIRNAME}/logs/bot.log')

    await bot_logs_channel.send(file=file)
    logger.info('fn > send_logs_file > OK')
