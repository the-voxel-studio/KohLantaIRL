import datetime
import signal
import sys
from os import name as os_name
from random import choice

import discord
from discord.ext import commands

import utils.pdf
from cogs.how_to import AllianceView
from config.values import (BOT_ID, CHANNEL_ID_BOT, CHANNEL_ID_BOT_PRIVATE,
                           CHANNEL_ID_INSCRIPTION, CHANNEL_ID_VOTE,
                           COLOR_ORANGE, COLOR_RED, EMOJI_ID_COLLIER,
                           EMOJIS_LIST, GUILD_ID, TOKEN)
from utils.bot import bot
from utils.game.alliances import purge_empty_alliances
from utils.game.players import join
from utils.game.timer import cancel_timer, start_new_timer
from utils.game.votes import EqualityView
from utils.log import send_log, send_logs_file
from utils.logging import get_logger
from utils.models import Player, setup_db_connection
from utils.punishments import timeout

# TODO Immunite collar : total review of the system

# ***** CONSTANTES *****
logger = get_logger(__name__)
COGS = ["cogs.admin", "cogs.how_to", "cogs.game.alliances", "cogs.game.steps", "cogs.game.votes", "cogs.game.eliminates","cogs.help", "cogs.punishments.muting"]

@bot.event
async def on_ready():
    for cog in COGS:
        await bot.load_extension(cog)
    setup_db_connection()
    time = datetime.datetime.now().strftime("%d/%m/%Y **%H:%M**")
    await purge_empty_alliances()
    await start_new_timer()
    if os_name == 'nt':
        await send_log("BOT restarted and ready", ":tools: mode : **DEV**", f":clock: time   : {time}", color="orange")
    else:
        await send_log("BOT restarted and ready", ":tools: mode : **PRODUCTION**", f":clock: time   : {time}", color="green")
    await send_logs_file()
    bot.add_view(EqualityView())
    bot.add_view(AllianceView())
    logger.info("Bot started and ready.")
    await bot.tree.sync()

@bot.event
async def on_message(message):
    await bot.process_commands(message) # Execute les commandes, même si le message a été envoyé en DM au robot
    if message.author.id != BOT_ID:
        if ":collierimmunite:" in message.content:
            logger.warning(f"Use of immunity collar in message by : {message.author} (id:{message.author.id}).")
            if not message.content.startswith("/"): await message.delete()
            logger.info("Sending a message reminding of the rules relating to the immunity collar.")
            embed=discord.Embed(title=f":robot: RAPPEL AUX JOUEURS :moyai:", description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.", color=COLOR_RED)
            await message.channel.send(embed=embed)
            await timeout(message.author,reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>")
        elif message.channel.id == CHANNEL_ID_INSCRIPTION:
            logger.info("New message in the join channel.")
            if not message.content.startswith("/"): 
                await message.delete() # Supprime le message s'il ne s'agit pas d'une commande (auquel cas le message a déjà été supprimé)
                await join(message)
        elif not message.guild:
            if not message.content.startswith("/"): 
                await message.author.send(choice([
                    "https://media.giphy.com/media/l2JhJGdpV4Uc3mffy/giphy.gif",
                    "https://tenor.com/view/shrek-donkey-dream-works-ane-attend-gif-23982857",
                    "https://tenor.com/bkf9g.gif",
                    "https://tenor.com/bxGXE.gif",
                    "https://tenor.com/bdWno.gif",
                    "https://tenor.com/St9l.gif"
                ]))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        if ctx.message.guild: await ctx.message.delete()
        logger.warning(f"CommandNotFound | Sent by {ctx.author} (id:{ctx.author.id}) | Content: {ctx.message.content}")
        embed=discord.Embed(title=f":robot: Commande inconnue :moyai:", description=f":warning: Veuillez vérifier l'orthographe", color=COLOR_ORANGE)
        await ctx.author.send(embed=embed)
    elif isinstance(error, commands.errors.MissingPermissions) or isinstance(error, discord.ext.commands.errors.MissingRole) or isinstance(error, discord.ext.commands.errors.MissingAnyRole):
        if ctx.message.guild: await ctx.message.delete()
        command = ctx.message.content.split(' ')[0]
        logger.warning(f"MissingPermissions | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: {command}")
        embed=discord.Embed(title=f":robot: Commande interdite :moyai:", description=f":no_entry: Vous n'avez pas les permissions nécessaires pour utiliser la commande !\n\nCommande : {command}", color=COLOR_RED)
        embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
        await ctx.author.send(embed=embed)
        embed=discord.Embed(title=f":robot: Commande bloquée :moyai:", description=f"sent by **{ctx.author.display_name}**\nattempted to use the command **{command}**", color=COLOR_RED)
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    elif isinstance(error, commands.errors.NoPrivateMessage):
        command = ctx.message.content.split(' ')[0]
        logger.warning(f"NoPrivateMessage | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: {command}")
        embed=discord.Embed(title=f":robot: Commande de serveur :moyai:", description=f":no_entry: Cette commande n'est pas disponible en message privé.\n\nCommande : {command}", color=COLOR_ORANGE)
        embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
        await ctx.author.send(embed=embed)
        embed=discord.Embed(title=f":robot: Commande MP bloquée :moyai:", description=f"sent by **{ctx.author.display_name}**\nattempted to use the command **{command}**", color=COLOR_ORANGE)
        await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    else:
        try: await ctx.message.delete()
        except: pass
        logger.error(f"Command error | Sent by {ctx.author} (id:{ctx.author.id}) | {error}")
        embed=discord.Embed(title=f":robot: Erreur :moyai:", description=f":warning: Une erreur est survenue lors de l'execution de cette commande.\n\nCommande : {ctx.message.content}", color=COLOR_ORANGE)
        await ctx.author.send(embed=embed)

# @bot.tree.error
# async def on_app_command_error(interaction: discord.Interaction, error):
#     if isinstance(error, discord.app_commands.errors.CommandNotFound):
#         logger.warning(f"CommandNotFound | Sent by {interaction.user} (id:{interaction.user.id}) | Content: {error}")
#         embed=discord.Embed(title=f":robot: Commande inconnue :moyai:", description=f":warning: Veuillez vérifier l'orthographe", color=COLOR_ORANGE)
#         await interaction.response.send_message(embed=embed)
#     elif isinstance(error.original, commands.errors.MissingPermissions) or isinstance(error.original, discord.ext.commands.errors.MissingRole) or isinstance(error.original, discord.ext.commands.errors.MissingAnyRole):
#         command = "/"+interaction.command.name
#         logger.warning(f"MissingPermissions | Sent by {interaction.user} (id:{interaction.user.id}) | Attempted to use the command: {command}")
#         embed=discord.Embed(title=f":robot: Commande interdite :moyai:", description=f":no_entry: Vous n'avez pas les permissions nécessaires pour utiliser la commande !", color=COLOR_RED)
#         embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
#         if interaction.response.is_done():
#             await interaction.followup.send(embed=embed)
#         else:
#             await interaction.response.send_message(embed=embed)
#         embed=discord.Embed(title=f":robot: Commande bloquée :moyai:", description=f"sent by **{interaction.user.display_name}**\nattempted to use the command **{command}**", color=COLOR_RED)
#         await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
#     elif isinstance(error.original, commands.errors.NoPrivateMessage):
#         command = "/"+interaction.command.name
#         logger.warning(f"NoPrivateMessage | Sent by {interaction.user} (id:{interaction.user.id}) | Attempted to use the command: {command}")
#         embed=discord.Embed(title=f":robot: Commande de serveur :moyai:", description=f":no_entry: Cette commande n'est pas disponible en message privé.", color=COLOR_ORANGE)
#         embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
#         if interaction.response.is_done():
#             await interaction.followup.send(embed=embed)
#         else:
#             await interaction.response.send_message(embed=embed)
#         embed=discord.Embed(title=f":robot: Commande MP bloquée :moyai:", description=f"sent by **{interaction.user.display_name}**\nattempted to use the command **{command}**", color=COLOR_ORANGE)
#         await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
#     else:
#         logger.error(f"Command error | Sent by {interaction.user} (id:{interaction.user.id}) | {error}")
#         embed=discord.Embed(title=f":robot: Erreur :moyai:", description=f":warning: Une erreur est survenue lors de l'execution de cette commande.", color=COLOR_ORANGE)
#         if interaction.response.is_done():
#             await interaction.followup.send(embed=embed)
#         else:
#             await interaction.response.send_message(embed=embed)

@bot.event
async def on_raw_reaction_add(payload):
    logger.info(f"New raw reaction | user: {payload.member} (id: {payload.member.id}) | msg id: {payload.message_id} | emoji: {chr(EMOJIS_LIST.index(payload.emoji.name)+65)}")
    player = Player(id = payload.user_id)
    user = payload.member
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    if user.id != bot.user.id:
        if type(payload.emoji) != str and payload.emoji.id == EMOJI_ID_COLLIER:
            await msg.remove_reaction(payload.emoji,  user)
            logger.warning(f"Use of immunity collar in reaction by : {user} (id:{user.id}).")
            logger.info("Sending a message reminding of the rules relating to the immunity collar.")
            embed=discord.Embed(title=f":robot: RAPPEL AUX JOUEURS :moyai:", description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.", color=COLOR_RED)
            await channel.send(embed=embed)
            await timeout(user,reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>")
        elif channel.id == CHANNEL_ID_VOTE and (not player.exists or not player.alive) :
            if not "Votant Final" in [r.name for r in user.roles]:
                await msg.remove_reaction(payload.emoji,  user)
                logger.warning(f"Vote received from an eliminated player. Sent by : {user} (id:{user.id}).")
                embed=discord.Embed(title=f":robot: Action interdite :moyai:", description=f":no_entry: Les aventuriers éliminés ne peuvent pas participer au vote.", color=COLOR_RED)
                await user.send(embed=embed)
        elif msg.channel.id == CHANNEL_ID_VOTE:
                users = []
                for react in msg.reactions:
                    users += [user async for user in react.users()]
                if users.count(user) > 1: 
                    await msg.remove_reaction(payload.emoji, user)

@bot.command()
async def pdf(ctx):
    file_path = utils.pdf.generate(5)
    file = discord.File(file_path)
    await ctx.send(content="Bonjour\nVoici un message de test avec un prototype du fichier .pdf généré après chaque vote.",file=file)

def signal_handler(sig, frame):
    logger.warning("Start of shutdown procedure.")
    cancel_timer()
    logger.warning("Complete shutdown procedure.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

bot.run(TOKEN) # Lancement du robot
