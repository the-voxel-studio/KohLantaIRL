import signal

import discord
import discord.ext.commands

from config.values import TOKEN
import discord.ext

from events.ready import on_ready_event
from events.message import on_message_event
from events.command_error import on_command_error_event
from events.app_command_error import on_app_command_error_event
from events.raw_reaction_add import on_raw_reaction_add_event

from utils.bot import bot
from utils.game.timer import cancel_timer
from utils.logging import get_logger

logger = get_logger(__name__)

COGS = [
    'cogs.admin',
    'cogs.how_to',
    'cogs.game.alliances',
    'cogs.game.steps',
    'cogs.game.votes',
    'cogs.game.immunity',
    'cogs.game.rewards',
    'cogs.help',
    'cogs.punishments.muting',
]


@bot.event
async def on_ready() -> None:
    """Lancement du robot"""

    await on_ready_event(COGS)


@bot.event
async def on_message(message) -> None:
    """Gestion des messages"""

    await on_message_event(message)


@bot.event
async def on_command_error(ctx, error) -> None:
    """Gestion des erreurs de commandes"""

    await on_command_error_event(ctx, error)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error) -> None:
    """Gestion des erreurs de commandes d'applications"""

    await on_app_command_error_event(interaction, error)


@bot.event
async def on_raw_reaction_add(payload) -> None:
    """Gestion des réactions ajoutées aux messages"""

    await on_raw_reaction_add_event(payload)


def signal_handler(sig, frame) -> None:
    """Gestion de l'interruption du programme"""

    logger.critical('Start of shutdown procedure.')
    cancel_timer()
    logger.critical('Complete shutdown procedure.')
    exit()


signal.signal(signal.SIGINT, signal_handler)  # Gestion de l'interruption du programme

bot.run(TOKEN)  # Lancement du robot
