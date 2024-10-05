import discord
from discord.ext import commands
import discord.ext.commands

from config.values import (CHANNEL_ID_BOT, COLOR_ORANGE, COLOR_RED, MODE)
import discord.ext

from utils.bot import bot
from utils.control import is_admin
from utils.logging import get_logger

logger = get_logger(__name__)


async def on_app_command_error_event(interaction: discord.Interaction, error) -> None:
    """Gestion des erreurs de commandes d'applications"""

    if MODE != 'PRODUCTION' and is_admin(interaction.user):
        raise error

    if isinstance(error, discord.app_commands.errors.CommandNotFound):
        logger.warning(
            f'CommandNotFound | Sent by {interaction.user} (id:{interaction.user.id}) | Content: {error}'
        )
        embed = discord.Embed(
            title=':robot: Commande inconnue :moyai:',
            description=":warning: Veuillez vérifier l'orthographe.\nJe ne comprend que les commandes proposées dans la liste défilante.",
            color=COLOR_ORANGE,
        )
        embed.set_image(
            url='https://media1.tenor.com/m/uNew5ACeNHkAAAAd/bescherelle-orthographe.gif'
        )
        await interaction.response.send_message(embed=embed)
    elif isinstance(error.original, commands.errors.MissingPermissions) \
            or isinstance(error.original, discord.ext.commands.errors.MissingRole) \
            or isinstance(error.original, discord.ext.commands.errors.MissingAnyRole):
        command = '/' + interaction.command.name
        logger.warning(
            f'MissingPermissions | Sent by {interaction.user} (id:{interaction.user.id}) | Attempted to use the command: {command}'
        )
        embed = discord.Embed(
            title=':robot: Commande interdite :moyai:',
            description=":no_entry: Vous n'avez pas les permissions nécessaires pour utiliser la commande !",
            color=COLOR_RED,
        )
        embed.set_footer(
            text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
        embed = discord.Embed(
            title=':robot: Commande bloquée :moyai:',
            description=f'sent by **{interaction.user.display_name}**\nattempted to use the command **{command}**',
            color=COLOR_RED,
        )
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    elif isinstance(error.original, commands.errors.NoPrivateMessage):
        command = '/' + interaction.command.name
        logger.warning(
            f'NoPrivateMessage | Sent by {interaction.user} (id:{interaction.user.id}) | Attempted to use the command: {command}'
        )
        embed = discord.Embed(
            title=':robot: Commande de serveur :moyai:',
            description=":no_entry: Cette commande n'est pas disponible en message privé.",
            color=COLOR_ORANGE,
        )
        embed.set_footer(
            text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
        embed = discord.Embed(
            title=':robot: Commande MP bloquée :moyai:',
            description=f'sent by **{interaction.user.display_name}**\nattempted to use the command **{command}**',
            color=COLOR_ORANGE,
        )
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    else:
        logger.error(
            f'Command error | Sent by {interaction.user} (id:{interaction.user.id}) | {error}'
        )
        embed = discord.Embed(
            title=':robot: Erreur :moyai:',
            description=":warning: Une erreur est survenue lors de l'execution de cette commande.",
            color=COLOR_ORANGE,
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
