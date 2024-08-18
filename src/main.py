import datetime
import signal
from random import choice

import discord
from discord.ext import commands
import discord.ext.commands

from cogs.how_to import AllianceView
from config.values import (BOT_ID, CHANNEL_ID_BOT, CHANNEL_ID_INSCRIPTION,
                           CHANNEL_ID_VOTE, COLOR_ORANGE, COLOR_RED,
                           EMOJI_ID_COLLIER, EMOJIS_LIST, MODE, TOKEN)
from database.game import Game
from database.player import Player
import discord.ext
from utils.bot import bot
from utils.control import is_admin
from utils.game.alliances import purge_empty_alliances
from utils.game.immunity.collar import (give_immunite_collar,
                                        move_immunite_collar_down)
from utils.game.players import join
from utils.game.timer import cancel_timer, start_new_timer
from utils.game.votes.close.normalEquality import EqualityView
from utils.log import send_log, send_logs_file
from utils.logging import get_logger
from utils.punishments import timeout

logger = get_logger(__name__)

COGS = [
    'cogs.admin',
    'cogs.how_to',
    'cogs.game.alliances',
    'cogs.game.steps',
    'cogs.game.votes',
    'cogs.game.immunity',
    'cogs.help',
    'cogs.punishments.muting',
]


@bot.event
async def on_ready() -> None:
    """Lancement du robot"""

    for cog in COGS:
        try:
            await bot.load_extension(cog)
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            logger.warning(f'Extension {cog} already loaded.')
    time = datetime.datetime.now().strftime('%d/%m/%Y **%H:%M**')
    deleted_count = await purge_empty_alliances()
    await start_new_timer()
    await send_logs_file()
    bot.add_view(EqualityView())
    bot.add_view(AllianceView())
    await move_immunite_collar_down()
    synced = await bot.tree.sync()
    bot_mode = MODE.upper() if MODE else 'PRODUCTION'
    color = 'green' if bot_mode == 'PRODUCTION' else 'orange'
    await send_log(
        'BOT restarted and ready',
        f':tools: mode : **{bot_mode}**',
        f':clock: time : {time}',
        f':handshake: empty alliances deleted : **{deleted_count}**',
        f':dividers: cogs loaded : **{len(COGS)}**',
        f':control_knobs: app commands : **{len(synced)}**',
        color=color,
    )
    logger.info('Bot started and ready.')


@bot.event
async def on_message(message) -> None:
    """Gestion des messages"""

    await bot.process_commands(
        message
    )  # Execute les commandes, même si le message a été envoyé en DM au robot
    if message.author.id != BOT_ID:
        if ':collierimmunite:' in message.content:
            logger.warning(
                f'Use of immunity collar in message by : {message.author} (id:{message.author.id}).'
            )
            if not message.content.startswith('/'):
                await message.delete()
            logger.info(
                'Sending a message reminding of the rules relating to the immunity collar.'
            )
            embed = discord.Embed(
                title=':robot: RAPPEL AUX JOUEURS :moyai:',
                description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.",
                color=COLOR_RED,
            )
            await message.channel.send(embed=embed)
            await timeout(
                message.author,
                reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>",
            )
        elif message.channel.id == CHANNEL_ID_INSCRIPTION:
            logger.info('New message in the join channel.')
            if not message.content.startswith('/'):
                await message.delete()  # Supprime le message s'il ne s'agit pas d'une commande (auquel cas le message a déjà été supprimé)
                await join(message)
        elif not message.guild:
            if not message.content.startswith('/'):
                embed = discord.Embed(
                    title=':robot: **Je ne comprend que les commandes !** :moyai:',
                    description='Je suis incapable de répondre à tout autre contenu...',
                    color=COLOR_ORANGE,
                )
                embed.set_image(
                    url=choice(
                        [
                            'https://media.giphy.com/media/l2JhJGdpV4Uc3mffy/giphy.gif',
                            'https://media1.tenor.com/m/1fLwP04D_IIAAAAC/shrek-donkey.gif',
                            'https://media1.tenor.com/m/m8euCQ_x3U8AAAAC/kaamelott-arthur.gif',
                            'https://media1.tenor.com/m/VAgfPZcM340AAAAd/bof-i-dont-mind.gif',
                            'https://media1.tenor.com/m/LjCBqxySvecAAAAd/huh-rabbit.gif',
                            'https://media1.tenor.com/m/13frun_noiAAAAAC/miss-j-j-alexander.gif',
                        ]
                    )
                )
                await message.author.send(embed=embed)


@bot.event
async def on_command_error(ctx, error) -> None:
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


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error) -> None:
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


@bot.event
async def on_raw_reaction_add(payload) -> None:
    """Gestion des réactions ajoutées aux messages"""

    if payload.emoji.name in EMOJIS_LIST:
        emoji = chr(EMOJIS_LIST.index(payload.emoji.name) + 65)
    else:
        emoji = 'not an alphabet emoji'
    logger.info(
        f'New raw reaction | user: {payload.member} (id: {payload.member.id}) | msg id: {payload.message_id} | emoji: {emoji}'
    )
    user = payload.member
    if user.id != bot.user.id:
        player = Player(id=payload.user_id)
        channel = bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if isinstance(payload.emoji, discord.partial_emoji.PartialEmoji) and payload.emoji.id == EMOJI_ID_COLLIER:
            await msg.remove_reaction(payload.emoji, user)
            if msg.id == Game.immunite_collar_msg_id and Player(id=user.id).object.alive:
                await msg.clear_reaction(
                    f'<:collierimmunite:{EMOJI_ID_COLLIER}>'
                )
                await give_immunite_collar(payload, player)
            else:
                logger.warning(
                    f'Use of immunity collar in reaction by : {user} (id:{user.id}).'
                )
                logger.info(
                    'Sending a message reminding of the rules relating to the immunity collar.'
                )
                embed = discord.Embed(
                    title=':robot: RAPPEL AUX JOUEURS :moyai:',
                    description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.",
                    color=COLOR_RED,
                )
                await channel.send(embed=embed, delete_after=20)
                await timeout(
                    user,
                    reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>",
                )
        elif channel.id == CHANNEL_ID_VOTE and (
            not player.object._id or not player.object.alive
        ):
            if 'Votant Final' not in [r.name for r in user.roles]:
                await msg.remove_reaction(payload.emoji, user)
                logger.warning(
                    f'Vote received from an eliminated player. Sent by : {user} (id:{user.id}).'
                )
                embed = discord.Embed(
                    title=':robot: Action interdite :moyai:',
                    description=':no_entry: Les aventuriers éliminés ne peuvent pas participer au vote.',
                    color=COLOR_RED,
                )
                await user.send(embed=embed)
        elif channel.id == CHANNEL_ID_VOTE:
            users = []
            for react in msg.reactions:
                users += [user async for user in react.users()]
            if users.count(user) > 1:
                await msg.remove_reaction(payload.emoji, user)


def signal_handler(sig, frame) -> None:
    """Gestion de l'interruption du programme"""

    logger.warning('Start of shutdown procedure.')
    cancel_timer()
    logger.warning('Complete shutdown procedure.')
    exit()


signal.signal(signal.SIGINT, signal_handler)  # Gestion de l'interruption du programme

bot.run(TOKEN)  # Lancement du robot
