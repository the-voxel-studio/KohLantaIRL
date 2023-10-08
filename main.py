import discord
from discord.ext import commands, tasks
import datetime
from os import environ, name as os_name, system
from models import Player, Alliance, Variables, NewPlayer, NewAlliance, setup_db_connection
from threading import Timer
import signal
import sys
from logging_setup import get_logger, setup_logger

last_vote_date = None
timer_thread = None

# ***** CONSTANTES *****
INTENTS = (intents) = discord.Intents.all()  # Importation des capacités de controle du robot
BOT = commands.Bot(command_prefix="/", description=f"Bot maitre du jeu", intents=INTENTS)  # Définition du préfixe des commandes, de la description Discord du bot et  application de ses capacités
EMOJIS_LIST = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯","🇰","🇱","🇲","🇳","🇴","🇵","🇶","🇷","🇸","🇹","🇺","🇻","🇼","🇽","🇾","🇿"] # Définition de la liste des émojis de réaction pour les votes
CHANNEL_ID_BOT = int(environ.get("CHANNEL_BOT"))
CHANNEL_ID_GENERAL = int(environ.get("CHANNEL_GENERAL"))
CHANNEL_ID_INSCRIPTION = int(environ.get("CHANNEL_INSCRIPTION"))
CHANNEL_ID_VOTE = int(environ.get("CHANNEL_VOTE"))
CHANNEL_ID_RESULTATS = int(environ.get("CHANNEL_RESULTATS"))
CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER = int(environ.get("CHANNEL_HELP_ALLIANCE_ADD_PLAYER"))
CATEGORIE_ID_ALLIANCES = int(environ.get("CATEGORIE_ALLIANCES"))
EMOJI_ID_COLLIER = int(environ.get("EMOJI_ID_COLLIER"))
USER_ID_ADMIN = int(environ.get("USER_ID_ADMIN"))
BOT_ID = int(environ.get("BOT_ID"))
GUILD_ID = int(environ.get("GUILD_ID"))
TOKEN = environ.get("TOKEN")
COLOR_GREEN = 0x008000
COLOR_ORANGE = 0xff7f00
COLOR_RED = 0xf00020

# ***** LOGGING *****
setup_logger()
logger = get_logger(__name__)

# ***** DECORATORS *****
def in_category(category_name):
    async def check(ctx):
        category_id = ctx.channel.category_id
        category = ctx.guild.get_channel(category_id)
        return category and category.name == category_name
    return commands.check(check)

# ***** BOT EVENTS *****
@BOT.event
async def on_ready():
    """Envoi d'un message de mise en ligne
    
    Cette fonction envoie simplement un message sur le channel de discussion du BOT pour informer les admin de sa mise en ligne.
    """
    setup_db_connection()
    time = datetime.datetime.now().strftime("%d/%m/%Y **%H:%M**")
    await start_new_timer()
    if os_name == 'nt':
        await send_log("BOT restarted and ready", ":tools: mode : **DEV**", f":clock: time   : {time}", color="orange")
    else:
        await send_log("BOT restarted and ready", ":tools: mode : **PRODUCTION**", f":clock: time   : {time}", color="green")
    logger.info("Bot started and ready.")

@BOT.event
async def on_message(message):
    await BOT.process_commands(message) # Execute les commandes, même si le message a été envoyé en DM au robot
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

@BOT.event
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
        await BOT.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    elif isinstance(error, commands.errors.NoPrivateMessage):
        command = ctx.message.content.split(' ')[0]
        logger.warning(f"NoPrivateMessage | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: {command}")
        embed=discord.Embed(title=f":robot: Commande de serveur :moyai:", description=f":no_entry: Cette commande n'est pas disponible en message privé.\n\nCommande : {command}", color=COLOR_ORANGE)
        embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
        await ctx.author.send(embed=embed)
        embed=discord.Embed(title=f":robot: Commande MP bloquée :moyai:", description=f"sent by **{ctx.author.display_name}**\nattempted to use the command **{command}**", color=COLOR_ORANGE)
        await BOT.get_channel(CHANNEL_ID_BOT).send(embed=embed)
    else:
        try: await ctx.message.delete()
        except: pass
        logger.error(f"Command error | Sent by {ctx.author} (id:{ctx.author.id}) | {error}")
        embed=discord.Embed(title=f":robot: Erreur :moyai:", description=f":warning: Une erreur est surveue lors de l'execution de cette commande.\n\nCommande : {ctx.message.content}", color=COLOR_ORANGE)
        await ctx.author.send(embed=embed)

@BOT.event
async def on_raw_reaction_add(payload):
    player = Player(id = payload.user_id)
    user = payload.member
    channel = BOT.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    if user.id != BOT.user.id:
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

# ***** BOT COMMANDS *****
@BOT.command(pass_context=True)
async def alliance(ctx, *args):
    if ctx.message.guild: await ctx.message.delete()
    player = Player(id=ctx.author.id)
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        logger.warning(f"PrivateMessage | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: /alliance")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Impossible d'effectuer l'action demandée : la commande *alliance* est disponible seulement en message privé avec le robot (ici).", color=COLOR_ORANGE)
        await ctx.author.send(embed=embed)
    elif not player.alive:
        logger.warning(f"EliminatedPlayer | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: /alliance")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Impossible d'effectuer l'action demandée : les joueurs éliminés ne peuvent pas créer d'alliance.", color=COLOR_ORANGE)
        await ctx.author.send(embed=embed)
    else:
        logger.info(f"New alliance creation started | Requested by {ctx.author} (id:{ctx.author.id}).")
        general_guild = BOT.get_guild(GUILD_ID)
        guild = discord.utils.get(general_guild.categories, id=CATEGORIE_ID_ALLIANCES)
        channel_name = args[0] if args[0] else "new_alliance"
        overwrites = {
            general_guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
        }
        new_text_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        new_voice_channel = await guild.create_voice_channel(channel_name, overwrites=overwrites)
        new_alliance = NewAlliance()
        new_alliance.text_id = new_text_channel.id
        new_alliance.voice_id = new_voice_channel.id
        new_alliance.name = channel_name
        new_alliance.creator = player._id
        new_alliance.save()
        embed=discord.Embed(title=f":robot: Nouvelle alliance :moyai:", description=f":white_check_mark: L'alliance {channel_name} a bien été créée : rendez-vous ici <#{new_text_channel.id}> pour y ajouter des joueurs.", color=COLOR_GREEN)
        await ctx.author.send(embed=embed)
        logger.info(f"New Alliance created | Requested by {ctx.author} (id:{ctx.author.id}) | Alliance text channel id: {new_text_channel.id}")

@BOT.command(pass_context=True)
@commands.guild_only()
@in_category("Alliances")
async def ajouter(ctx, *args):
    if ctx.message.guild: await ctx.message.delete()
    if len(args) == 2:
        logger.info(f"New alliance member addition started | Requested by {ctx.author} (id:{ctx.author.id}) | Alliance text channel id: {ctx.channel.id}")
        name = f"{args[0]} {args[1]}"
        player = Player(nickname=name)
        if player.id != 0:
            if player.alive:
                user = BOT.get_user(player.id)
                alliance = Alliance(text_id=ctx.channel.id)
                perms = ctx.channel.overwrites_for(user)
                perms.read_messages = True
                await ctx.channel.set_permissions(user, overwrite=perms)
                voice_channel = BOT.get_channel(alliance.voice_id)
                perms = voice_channel.overwrites_for(user)
                perms.read_messages = True
                await voice_channel.set_permissions(user, overwrite=perms)
                alliance.add_member(player._id)
                embed=discord.Embed(title=f":robot: Nouvelle alliance :moyai:", description=f":new: Vous avez été ajouté à l'alliance <#{ctx.channel.id}> par <@{ctx.author.id}> !", color=COLOR_GREEN)
                await user.send(embed=embed)
                embed=discord.Embed(title=f":robot: Nouveau membre :moyai:", description=f":new: <@{ctx.author.id}> a ajouté <@{player.id}> à l'alliance !", color=COLOR_GREEN)
                await ctx.send(embed=embed)
                logger.info(f"New alliance member added | Requested by {ctx.author} (id:{ctx.author.id}) | New member: {player} (id:{player.id}) | Alliance text channel id: {ctx.channel.id}")
            else:
                logger.warning(f"NewAllianceMemberNotAlive | Requested by {ctx.author} (id:{ctx.author.id}) | New member: {player} (id:{player.id}) | Alliance text channel id: {ctx.channel.id}")
                embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Le joueur spécifié a été éliminé lors d'un vote, il est donc impossible de l'ajouter à une alliance.", color=COLOR_ORANGE)
                await ctx.send(embed=embed)
        else:
            logger.warning(f"NewAllianceMemberNotFound | Requested by {ctx.author} (id:{ctx.author.id}) | New member list: {args} | Alliance text channel id: {ctx.channel.id}")
            embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Le joueur spécifié est introuvable. Veuillez vérifier le fonctionnement de cette commande ici <#{CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER}>", color=COLOR_ORANGE)
            await ctx.send(embed=embed)
    else:
        logger.warning(f"NewAllianceMemberBadFormat | Requested by {ctx.author} (id:{ctx.author.id}) | New member list: {args} | Alliance text channel id: {ctx.channel.id}")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Le format requis n'est pas respecté. Veuillez vérifier le fonctionnement de cette commande ici <#{CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER}>", color=COLOR_ORANGE)
        await ctx.send(embed=embed)

@BOT.command(pass_context=True)
@commands.guild_only()
@in_category("Alliances")
async def supprimer(ctx, member: discord.Member, *args):
    if ctx.message.guild: await ctx.message.delete()
    logger.info(f"Alliance member removing started | Requested by {ctx.author} (id:{ctx.author.id}) | Member: {member} (id:{member.id}) | Alliance text channel id: {ctx.channel.id}")
    player = Player(id=member.id)
    alliance = Alliance(text_id=ctx.channel.id)
    await ctx.channel.set_permissions(member, overwrite=None)
    await BOT.get_channel(alliance.voice_id).set_permissions(member, overwrite=None)
    alliance.remove_member(player._id)
    embed=discord.Embed(title=f":robot: Expulsion d'une alliance :moyai:", description=f":warning: Vous avez été supprimé de l'alliance *{ctx.channel.name}* par <@{ctx.author.id}> !", color=COLOR_ORANGE)
    await member.send(embed=embed)
    embed=discord.Embed(title=f":robot: Expulsion :moyai:", description=f":warning: <@{ctx.author.id}> a supprimé <@{player.id}> de l'alliance !", color=COLOR_ORANGE)
    await ctx.send(embed=embed)
    logger.info(f"Alliance member removed | Requested by {ctx.author} (id:{ctx.author.id}) | Member: {member} (id:{member.id}) | Alliance text channel id: {ctx.channel.id}")

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def clear(ctx, amount=1):
    if ctx.message.guild: await ctx.message.delete()
    logger.info(f"Partial channel clearing | Requested by {ctx.author} (id:{ctx.author.id}) | Number: {amount} | Channel id: {ctx.channel.id}")
    await ctx.channel.purge(limit=amount)

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def open_vote(ctx):
    await ctx.message.delete()
    logger.info(f"Vote opening | Requested by {ctx.author} (id:{ctx.author.id}).")
    await show_vote_msg()

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def close_vote(ctx): 
    await ctx.message.delete()
    logger.info(f"Vote closing | Requested by {ctx.author} (id:{ctx.author.id}).")
    await retrieval_of_results()

@BOT.command(pass_context = True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def mute(ctx, member: discord.Member, minutes=10, reason=None):
    await ctx.message.delete()
    logger.info(f"Member muting | Requested by {ctx.author} (id:{ctx.author.id}) | Member: {member} (id:{member.id})")
    await timeout(member,author=ctx.author,minutes=minutes,reason=reason)

@BOT.command(pass_context = True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def unmute(ctx, member: discord.Member, minutes=10, reason=None):
    await ctx.message.delete()
    logger.info(f"Member unmuting | Requested by {ctx.author} (id:{ctx.author.id}) | Member: {member} (id:{member.id})")
    await member.timeout(None)
    embed=discord.Embed(title=f":robot: {member} Unmuted :moyai:", description=f"by **{ctx.author}**", color=COLOR_GREEN)
    await BOT.get_channel(CHANNEL_ID_BOT).send(embed=embed)

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def send(ctx, channel: discord.TextChannel, content: str, color: str ="green"):
    await ctx.message.delete()
    logger.info(f"Important message sending | Requested by {ctx.author} (id:{ctx.author.id}) | Channel id: {channel.id} | Color: {color} | Content: {content}")
    embed=discord.Embed(title=f":robot: Information de {ctx.author.display_name} :moyai:", description=content, color=eval("COLOR_"+color.upper()))
    await channel.send(embed=embed)

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def eliminer(ctx, member: discord.Member):
    await ctx.message.delete()
    logger.info(f"Member elimination started | Requested by {ctx.author} (id:{ctx.author.id}) | Member: {member} (id:{member.id})")
    eliminated = Player(id=member.id)
    players = Player(option="living")
    players_list = players.list
    embed = discord.Embed(
        title=f"**{eliminated.nickname}**",
        description=f"Le dernier éliminé a décidé de l'éliminer et sa sentence est irrévocable !",
        color=15548997
    )
    embed.set_author(name="Résultat du conseil",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
    embed.set_thumbnail(url="https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp")
    embed.add_field(name=f"Cet aventurier a reçu le vote du dernier éliminé suite à une égalité.", value=f"Il reste {len(players_list)-1} aventuriers en jeu.", inline=True)
    channel = BOT.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed)
    guild = BOT.get_guild(GUILD_ID)
    member = guild.get_member(eliminated.id)
    role = discord.utils.get(guild.roles, name="Joueur")
    new_role = discord.utils.get(guild.roles, name="Eliminé")
    await member.remove_roles(role)
    await member.add_roles(new_role)
    eliminated.eliminate()
    logger.info(f"Member eliminated | Requested by {ctx.author} (id:{ctx.author.id}) | Member: {member} (id:{member.id})")

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def start(ctx):
    await ctx.message.delete()
    logger.info(f"Game start | Requested by {ctx.author} (id:{ctx.author.id}).")
    Variables.start_game()    

@BOT.command(pass_context=True)
@commands.guild_only()
@commands.has_any_role("Admin")
async def restart(ctx):
    await ctx.message.delete()
    logger.info(f"Preparing for manual reboot. | Requested by {ctx.author} (id:{ctx.author.id})")
    timer_thread.cancel()
    await send_log("Redémarrage manuel en cours", f"by **{ctx.author.display_name}**", color="orange")
    logger.info("Ready to reboot.")
    system("sudo reboot")

# ***** TIMER THREAD *****
async def timed_action():
    logger.info('A thread timer has ended.')
    time = datetime.datetime.now()
    hour = int(time.strftime("%H"))
    if hour == 1:
        logger.info("Preparing for automatic reboot.")
        timer_thread.cancel()
        await send_log("Redémarrage automatique en cours", color="orange")
        logger.info("Ready to reboot.")
        system("sudo reboot")
    elif hour == 18 and Variables.get_state() == 1:
        await show_vote_msg()
    elif hour == 21 and Variables.get_vote_msg_id() != 0 and Variables.get_state() == 1:
        await retrieval_of_results()
    elif hour == 0 and Variables.get_vote_msg_id() != 0 and Variables.get_state() == 3:
        # Variables.game_end()
        await retrieval_of_results()
    await start_new_timer()

# ***** FONCTIONS *****
async def timeout(member: discord.User, **kwargs):
    if member.id not in [USER_ID_ADMIN,BOT_ID]:
        logger.info(f"fn > timeout > start | Member: {member} (id:{member.id})")
        author = kwargs.get("author", "Denis Brogniart")
        reason_arg = kwargs.get("reason", "unknown")
        reason = reason_arg if reason_arg else "unknown"
        delta = datetime.timedelta(minutes=kwargs.get("minutes",10))
        logger.info(f"fn > timeout > options | Member: {member} (id:{member.id}) | Requested by: {author} | Timedelta: {delta} | Reason: {reason}")
        await member.timeout(delta,reason=reason)
        embed=discord.Embed(title=f":robot: {member} Muted! :moyai:", description=f"by **{author}**\nbecause of **{reason}**\nfor **{delta}**", color=COLOR_RED)
        await BOT.get_channel(CHANNEL_ID_BOT).send(embed=embed)
        logger.info(f"fn > timeout > OK | Member: {member} (id:{member.id})")

async def show_vote_msg():# TODO add logs
    players = Player(option="living")
    players_list = players.list
    if len(players_list) > 2:
        embed = discord.Embed(title=f"Qui souhaitez-vous éliminer ce soir ?",description=f"Vous avez jusqu'à 21h ce soir pour choisir la personne que vous souhaitez éliminer en réagissant à ce message.",color=0x109319)
        embed.set_author(name="Le conseil",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
    else:
        embed = discord.Embed(title=f"Qui doit remporter cette saison ?",description=f"Vous avez jusqu'à 23h59 ce soir pour choisir la personne que remportera cette saison en réagissant à ce message.",color=0x109319)
        embed.set_author(name="La Finale",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
        guild = BOT.get_guild(GUILD_ID)
        v_role = discord.utils.get(guild.roles, name="Votant Final") # Récupération du role "Votant final"
        f_role = discord.utils.get(guild.roles, name="Finaliste") # Récupération du role "Finaliste"
        voters = Player(option="eliminated")
        voters_list = voters.list
        for v in voters_list:
            await guild.get_member(v.get("id",0)).add_roles(v_role) # Assignation du nouveau role
        category = discord.utils.get(guild.categories, name="Alliances")
        for f in players_list:
            await guild.get_member(f.get("id",0)).add_roles(f_role) # Assignation du nouveau role
            for channel in category.channels:
                user = BOT.get_user(f.get("id",0))
                perms = channel.overwrites_for(user)
                perms.read_messages = False
                await channel.set_permissions(user, overwrite=perms)
    embed.set_thumbnail(url="https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp")
    embed.set_footer(text="Choisissez la personne pour qui vous votez en cliquant sur une des cases ci-dessous.\nVous souhaitez savoir combien de personnes ont voté pour une personne ? Il suffit de soustraire 1 aux nombres inscrits ci-dessous. ")
    reactions = []
    for i, pl in enumerate(players_list):
        embed.add_field(name=pl.get("nickname", "unknown"), value=f"Choisir le logo {EMOJIS_LIST[i]}", inline=True)
        Player(id=pl.get("id")).set_letter(chr(i+65))
        reactions.append(EMOJIS_LIST[i])
    channel = BOT.get_channel(CHANNEL_ID_VOTE)
    msg = await channel.send(embed=embed)
    Variables.set_vote_msg_id(msg.id)
    for r in reactions:
        await msg.add_reaction(r)

async def retrieval_of_results():# TODO add logs
    channel = BOT.get_channel(CHANNEL_ID_VOTE)
    # try:
    msg = await channel.fetch_message(Variables.get_vote_msg_id())
    reactions = msg.reactions ; reactions_list = {}
    for r in msg.reactions:
        async for u in r.users():
            if u.id != BOT_ID:
                if u.id not in reactions_list:
                    reactions_list[u.id] = [r.emoji]
                elif r.emoji not in reactions_list[u.id]:
                    reactions_list[u.id].append(r.emoji)
    await msg.delete()
    Variables.set_vote_msg_id(0)
    embed=discord.Embed(title=f":robot: Tricherie détectée :moyai:", description=f":no_entry: Vous avez voté pour plusieurs personnes en même temps.\nTous vos votes ont donc été annulés pour ce dernier vote.\nPar ailleurs, vous reçevez une sanction de type ban pendant 30 minutes.", color=COLOR_RED)
    embed.set_footer(text="Cette décision automatique n'est pas contestable. Vous pouvez néanmoins contacter un administrateur en MP pour signaler un éventuel problème.")
    for uid, emojis in reactions_list.items():
        if len(emojis) > 1:
            for react in reactions:
                if react.emoji in emojis: react.count -= 1
            user = await BOT.fetch_user(uid)
            await user.send(embed=embed)
            guild = BOT.get_guild(GUILD_ID)
            member = guild.get_member(uid)
            await timeout(member,reason=f"Tentative de triche au vote.",minutes=30)
    max_reactions = [] ; max_count = 0
    for reaction in reactions:
        if reaction.count > max_count:
            max_count = reaction.count
            max_reactions = [reaction.emoji]
        elif reaction.count == max_count:
            max_reactions.append(reaction.emoji)
    if len(max_reactions) == 1:
        eliminated = Player(letter=chr(EMOJIS_LIST.index(max_reactions[0])+65))
        nb_remaining_players = len(reactions)-1
        embed = discord.Embed(
            title=f"**{eliminated.nickname}**",
            description=f"Les aventuriers de la tribu ont décidé de l'éliminer et leur sentence est irrévocable !",
            color=15548997
        )
        embed.set_author(name="Résultat du conseil",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
        embed.set_thumbnail(url="https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp")
        value = f"Il reste {nb_remaining_players} aventuriers en jeu." if nb_remaining_players != 1 else ""
        embed.add_field(name=f"Cet aventurier a reçu {max_count-1} votes.", value=value, inline=True)
        channel = BOT.get_channel(CHANNEL_ID_RESULTATS)
        await channel.send(embed=embed)
        guild = BOT.get_guild(GUILD_ID)
        member = guild.get_member(eliminated.id)
        role = discord.utils.get(guild.roles, name="Joueur")
        new_role = discord.utils.get(guild.roles, name="Eliminé")
        await member.remove_roles(role)
        await member.add_roles(new_role)
        eliminated.eliminate()
        if nb_remaining_players == 1 : Variables.wait_for_last_vote()
        # FIXME sup membre éliminé de ses alliances
        # TODO save "death_council_number" in models
        # TODO send MP to eliminated player
        # TODO send who voted to this player (or complet details)
        # TODO sup alliances à membre unique
    else:
        embed = discord.Embed(
            title=f"**Egalité**",
            description=f"Les aventuriers de la tribu n'ont pas sus se décider !",
            color=9807270
        )
        embed.set_author(name="Résultat du conseil",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
        embed.set_thumbnail(url="https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp")
        embed.add_field(name="La dernière personne éliminée va être contactée pas un administrateur afin de trancher entre les personnes atant actuellement à égalité.", value=f"Vous serez avertis via ce canal dès la décision prise et saisie.", inline=True)
        channel = BOT.get_channel(CHANNEL_ID_RESULTATS)
        await channel.send(embed=embed)
    # except:
    #     pass

async def join(message):
    """Inscription au jeu
    
    Cette fonctione permet de s'inscrire dans le jeu.
    Elle récupère le prenom et l'initiale fournie, crée l'arboréscence dans la base de donnée et attribue le role de "joueur"
    
    Parameters
    ----------
    message:
		Objet message envoyé dans le channel "inscription"
        Contient le contenu, l'auteur, le channel, la guild...
    """
    logger.info(f"fn > join > start | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
    args = message.content.split(" ") # Découpe du texte du contenu en fonciton des espaces
    player = message.author # Récupère le joueur ayant envoyé la commande
    if Variables.get_state(): # Vérification du statut du jeu : les inscriptions ne doivent pas être closes
        logger.warning(f"fn > join > GameAlreadyStarted | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: La partie a déjà débutée", color=COLOR_ORANGE)
        await player.send(embed=embed)
    elif Player(id=player.id).exists: # Recherche de l'identifiant unique Discord du joueur pour vérifier qu'il n'est pas déjà inscrit
        logger.warning(f"fn > join > PlayerAlreadyJoined | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
        embed=discord.Embed(title=f":robot: Action inutile :moyai:", description=f":white_check_mark: Vous êtes déjà inscrit à cette partie.", color=COLOR_GREEN)
        embed.set_footer(text="En cas de problème, contacter un administrateur en MP.")
        await player.send(embed=embed)
    elif len(args) != 2 or len(args[0]) == 0 or len(args[1]) != 1: # Vérification du format des éléments fournis : deux éléments dont la longeur du premier doit être supérieure à 0 et du second doit être égale à 1
        logger.warning(f"fn > join > BadFormat | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
        embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Vous devez renseigner votre prénom et initiale de nom comme suis : `Prénom N`\nDe plus, le prénom ne peut contenir d'espaces. Si besoin, utilisez des *-* .", color=COLOR_ORANGE)
        await player.send(embed=embed)
    else:
        nickname = "{} {}".format(args[0], args[1]) # Création d'une seule chaine de caractère sous le format "Arthur D"
        try:
            await player.edit(nick=nickname) # Tentative de renommage du joueur sur Discord sous le format ci-dessus
        except:
            logger.error(f"fn > join > PlayerEditError | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")
            embed=discord.Embed(title=f":robot: Faible erreur :moyai:", description=f":warning: Une erreur est survenue lors du changement de votre nom sur le serveur : Veuillez contacter <@{USER_ID_ADMIN}> pour qu'il effectue la modification manuellement.\nPas d'inquiétude, le processus d'inscription continue normalement, cela n'auras aucun impact.", color=COLOR_ORANGE) # En cas d'erreur (il s'agit d'une commande un peu capricieuse)
            await player.send(embed=embed)
        new_player = NewPlayer() # Création d'un nouvel objet "joueur" dans la base de donnée
        new_player.id = player.id
        new_player.nickname = nickname
        new_player.save() # Enregistrement du joueur dans la base de données
        role = discord.utils.get(message.guild.roles, name="Joueur") # Récupération du role "joueur"
        await player.add_roles(role) # Assignation du nouveau role
        embed=discord.Embed(title=f":robot: Bienvenue ! :moyai:", description=f":white_check_mark: Bienvenue dans cette saison de Koh Lanta IRL !\nTon compte a été paramétré avec succès, nous te laissons découvrir les différents salons et les différentes actions que tu peux effectuer sur ce serveur.\nA très vite !", color=COLOR_GREEN)
        await player.send(embed=embed)
        embed=discord.Embed(title=f":confetti_ball: On souhaite la bienvenue à **{nickname}** qui participera à la prochaine saison de Koh Lanta IRL !:confetti_ball:", color=COLOR_GREEN)
        await BOT.get_channel(CHANNEL_ID_GENERAL).send(embed=embed)
        logger.info(f"fn > join > OK | Requested by: {message.author} (id:{message.author.id}) | Message: {message.content}")

async def set_inscription_infos():
    embed = discord.Embed(title=f"Vous souhaitez nous rejoindre ?",description=f"Vous pouvez dès à présent vous inscrire à la prochaine saison de KohLanta IRL !",color=0x109319)
    embed.set_author(name="Inscription",icon_url="https://cdn.discordapp.com/avatars/1139673903678095400/fe3974836708aab020a743b2700e87e4.webp?size=100")
    embed.set_thumbnail(url="https://photos.tf1.fr/1200/720/vignette-16-9-4d6adf-748cc7-0@1x.webp")
    embed.add_field(name="Entrez votre prénom et l\'initale de votre nom dans le champ ci-dessous.", value="Exemple : Arthur D", inline=False)  
    embed.add_field(name="Le prénom ne doit pas contenir d\'espace ou de caractère spécial autre que \"-\".", value="Vous avez un prénom composé ? Remplacez les espaces par un caractère \"-\".", inline=False)  
    embed.set_footer(text=f"Vous rencontrez un problème ? Contactez dès que possible un administrateur.")
    channel = BOT.get_channel(CHANNEL_ID_INSCRIPTION)
    await channel.send(embed=embed)

async def send_log(title: str, *args, **kwargs):
    bot_channel = BOT.get_channel(CHANNEL_ID_BOT)
    if len(args) != 0:
        color = kwargs.get("color", "ORANGE").upper()
        embed=discord.Embed(title=f":robot: {title} :moyai:", color=eval("COLOR_"+color))
        embed.description = "\n".join(args)
        await bot_channel.send(embed=embed)
    else:
        await bot_channel.send(title)

async def start_new_timer():
    global timer_thread
    time = datetime.datetime.today()
    next_time = time.replace(day=time.day, hour=time.hour, minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    delta = (next_time - time).total_seconds()
    timer_thread = Timer(delta, timed_action)
    timer_thread.start()
    logger.info('New thread timer triggered.')

def signal_handler(sig, frame):
    logger.warning("Start of shutdown procedure.")
    timer_thread.cancel()
    logger.warning("Complete shutdown procedure.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
BOT.run(TOKEN) # Lancement du roBOT
