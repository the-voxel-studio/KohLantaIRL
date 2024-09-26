import discord
from discord.ext import commands
import discord.ext.commands

from config.values import (CHANNEL_ID_BOT, COLOR_ORANGE, COLOR_RED, MODE)
import discord.ext

from utils.bot import bot
from utils.control import is_admin
from utils.logging import get_logger

logger = get_logger(__name__)


async def on_command_error_event(ctx, error) -> None:
    """Gestion des erreurs de commandes"""

    if MODE != 'PRODUCTION' and is_admin(ctx.author):
        raise error

    if isinstance(error, commands.errors.CommandNotFound):
        if ctx.message.guild:
            await ctx.message.delete()
        logger.warning(
            f'CommandNotFound | Sent by {ctx.author} (id:{ctx.author.id}) | Content: {ctx.message.content}'
        )
        embed = discord.Embed(
            title=':robot: Commande inconnue :moyai:',
            description=":warning: Veuillez vérifier l'orthographe.\nJe ne comprend que les commandes proposées dans la liste défilante.",
            color=COLOR_ORANGE,
        )
        embed.set_image(
            url='https://media1.tenor.com/m/uNew5ACeNHkAAAAd/bescherelle-orthographe.gif'
        )
        await ctx.author.send(embed=embed)
    elif isinstance(error, commands.errors.MissingPermissions) \
            or isinstance(error, discord.ext.commands.errors.MissingRole) \
            or isinstance(error, discord.ext.commands.errors.MissingAnyRole):
        if ctx.message.guild:
            await ctx.message.delete()
        command = ctx.message.content.split(' ')[0]
        logger.warning(
            f'MissingPermissions | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: {command}'
        )
        embed = discord.Embed(
            title=':robot: Commande interdite :moyai:',
            description=f":no_entry: Vous n'avez pas les permissions nécessaires pour utiliser la commande !\n\nCommande : {command}",
            color=COLOR_RED,
        )
        embed.set_footer(
            text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
        )
        await ctx.author.send(embed=embed)
        embed = discord.Embed(
            title=':robot: Commande bloquée :moyai:',
            description=f'sent by **{ctx.author.display_name}**\nattempted to use the command **{command}**',
            color=COLOR_RED,
        )
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    elif isinstance(error, commands.errors.NoPrivateMessage):
        command = ctx.message.content.split(' ')[0]
        logger.warning(
            f'NoPrivateMessage | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: {command}'
        )
        embed = discord.Embed(
            title=':robot: Commande de serveur :moyai:',
            description=f":no_entry: Cette commande n'est pas disponible en message privé.\n\nCommande : {command}",
            color=COLOR_ORANGE,
        )
        embed.set_footer(
            text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
        )
        await ctx.author.send(embed=embed)
        embed = discord.Embed(
            title=':robot: Commande MP bloquée :moyai:',
            description=f'sent by **{ctx.author.display_name}**\nattempted to use the command **{command}**',
            color=COLOR_ORANGE,
        )
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    else:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        logger.error(
            f'Command error | Sent by {ctx.author} (id:{ctx.author.id}) | {error}'
        )
        embed = discord.Embed(
            title=':robot: Erreur :moyai:',
            description=f":warning: Une erreur est survenue lors de l'execution de cette commande.\n\nCommande : {ctx.message.content}",
            color=COLOR_ORANGE,
        )
        await ctx.author.send(embed=embed)
