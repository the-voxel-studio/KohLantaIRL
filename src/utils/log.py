import os
from pathlib import Path

import discord

from config.values import (CHANNEL_ID_BOT, CHANNEL_ID_BOT_LOGS, COLOR_GREEN,
                           COLOR_ORANGE, COLOR_RED, EMOJI_ID_COLLIER)
from utils.bot import bot
from utils.logging import get_logger, FILE_LOG_NAME
from database.player import PlayerList

logger = get_logger(__name__)
COLOR_GREEN, COLOR_ORANGE, COLOR_RED  # COULEURS OBLIGATOIRES (utilisation de la fonction eval)
DIRNAME = Path(__file__).parent.parent.parent


async def send_log(title: str, *args, **kwargs):
    """Send a log to the bot channel."""

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
    """Send the logs file to the bot logs channel."""

    logger.info('fn > send_logs_file > start')
    bot_logs_channel = bot.get_channel(CHANNEL_ID_BOT_LOGS)
    if os.name == 'nt':
        file = discord.File(f'{DIRNAME}\\logs\\{FILE_LOG_NAME}')
    else:
        file = discord.File(f'{DIRNAME}/logs/{FILE_LOG_NAME}')

    await bot_logs_channel.send(file=file)
    logger.info('fn > send_logs_file > OK')


async def send_vote_log_to_admin(
        nb_cast_votes: int,
        nb_cheaters: int,
        nb_collar_immunized_loosers: int,
        nb_ephemerally_immunized_loosers: int,
        state: str = 'unknown',
        nb_tied_players: int = 0
        ) -> None:
    """Send the vote log to the bot logs channel (except spoil)."""

    logger.info('fn > send_vote_log_to_admin > start')
    bot_channel = bot.get_channel(CHANNEL_ID_BOT)
    args = [
        f':page_facing_up: **État du vote**: `{state}`',
        f':busts_in_silhouette: nombre de votants: `{len(PlayerList(alive=True))}`',
        f':cross: joueurs éliminés: `{len(PlayerList(alive=False))}`',
        f':envelope_with_arrow: votes exprimés: `{nb_cast_votes}`',
        f':ninja: tricheurs: `{nb_cheaters}`',
        f'<:collierimmunite:{EMOJI_ID_COLLIER}> joueurs immunisés par collier: `{nb_collar_immunized_loosers}`',
        f':shield: joueurs immunisés éphémèrement: `{nb_ephemerally_immunized_loosers}`',
        f':balance_scale: joueurs à égalité: `{nb_tied_players}`',
    ]
    embed = discord.Embed(
        title=':robot: Vote Infos :moyai:',
        description='\n'.join(args),
        color=COLOR_ORANGE,
    )
    embed.set_footer(text='Ces données sont strictement confidentielles et leur accès est réservé aux administrateurs du serveur.')

    await bot_channel.send(embed=embed)
    logger.info('fn > send_vote_log_to_admin > OK')
