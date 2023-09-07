_M='%Y/%m/%d'
_L='Eliminé'
_K='living'
_J='Votant Final'
_I='unknown'
_H='Joueur'
_G='Résultat du conseil'
_F='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
_E='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp'
_D=False
_C=None
_B='Admin'
_A=True
import discord
from discord.ext import commands,tasks
import datetime
from os import environ,name as os_name
from models import Player,Alliance,Variables,NewPlayer,NewAlliance
intents=intents=discord.Intents.all()
bot=commands.Bot(command_prefix='/',description=f"Bot maitre du jeu",intents=intents)
emojis=['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿']
last_vote_date=_C
CHANNEL_ID_BOT=int(environ.get('CHANNEL_BOT'))
CHANNEL_ID_GENERAL=int(environ.get('CHANNEL_GENERAL'))
CHANNEL_ID_INSCRIPTION=int(environ.get('CHANNEL_INSCRIPTION'))
CHANNEL_ID_VOTE=int(environ.get('CHANNEL_VOTE'))
CHANNEL_ID_RESULTATS=int(environ.get('CHANNEL_RESULTATS'))
CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER=int(environ.get('CHANNEL_HELP_ALLIANCE_ADD_PLAYER'))
CATEGORIE_ID_ALLIANCES=int(environ.get('CATEGORIE_ALLIANCES'))
EMOJI_ID_COLLIER=int(environ.get('EMOJI_ID_COLLIER'))
USER_ID_ADMIN=int(environ.get('USER_ID_ADMIN'))
BOT_ID=int(environ.get('BOT_ID'))
GUILD_ID=int(environ.get('GUILD_ID'))
TOKEN=environ.get('TOKEN')
COLOR_GREEN=32768
COLOR_ORANGE=16744192
COLOR_RED=15728672
@bot.event
async def on_ready():
        A=':robot: Bot restarted and ready :moyai:';bot_channel=bot.get_channel(CHANNEL_ID_BOT);time=datetime.datetime.now().strftime('%d/%m/%Y **%H:%M**')
        if os_name=='nt':embed=discord.Embed(title=A,description=f":tools: mode : **DEV**\n:clock: time   : {time}",color=COLOR_ORANGE);await bot_channel.send(embed=embed)
        else:embed=discord.Embed(title=A,description=f":white_check_mark: mode : **PRODUCTION**\n:clock: time   : {time}",color=COLOR_GREEN);await bot_channel.send(embed=embed)
        await shedules_loop()
@bot.event
async def on_message(message):
        await bot.process_commands(message)
        if message.author.id!=BOT_ID:
                if':collierimmunite:'in message.content:
                        if not message.content.startswith('/'):await message.delete()
                        embed=discord.Embed(title=f":robot: RAPPEL AUX JOUEURS :moyai:",description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.",color=COLOR_RED);await message.channel.send(embed=embed);await timeout(message.author,reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>")
                elif message.channel.id==CHANNEL_ID_INSCRIPTION:
                        if not message.content.startswith('/'):await message.delete();await join(message)
@bot.event
async def on_command_error(ctx,error):
        print(error)
        if isinstance(error,discord.ext.commands.errors.CommandNotFound):
                if ctx.message.guild:await ctx.message.delete()
                embed=discord.Embed(title=f":robot: Commande inconnue :moyai:",description=f":warning: Veuillez vérifier l'orthographe",color=COLOR_ORANGE);await ctx.author.send(embed=embed)
        elif isinstance(error,discord.ext.commands.errors.MissingPermissions)or isinstance(error,discord.ext.commands.errors.MissingRole)or isinstance(error,discord.ext.commands.errors.MissingAnyRole):
                if ctx.message.guild:await ctx.message.delete()
                command=ctx.message.content.split(' ')[0];embed=discord.Embed(title=f":robot: Commande interdite :moyai:",description=f":no_entry: Vous n'avez pas les permissions nécessaires pour utiliser la commande !\n\nCommande : {command}",color=COLOR_RED);embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.");await ctx.author.send(embed=embed);embed=discord.Embed(title=f":robot: Commande bloquée :moyai:",description=f"sent by **{ctx.author.display_name}**\nattempted to use the command **{command}**",color=COLOR_RED);await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
        else:
                try:await ctx.message.delete()
                except:pass
                embed=discord.Embed(title=f":robot: Erreur :moyai:",description=f":warning: Une erreur est surveue lors de l'execution de cette commande.\n\nCommande : {ctx.message.content}",color=COLOR_ORANGE);await ctx.author.send(embed=embed)
@bot.event
async def on_raw_reaction_add(payload):
        player=Player(id=payload.user_id);user=payload.member;channel=bot.get_channel(payload.channel_id);msg=await channel.fetch_message(payload.message_id)
        if user.id!=bot.user.id:
                if type(payload.emoji)!=str and payload.emoji.id==EMOJI_ID_COLLIER:await msg.remove_reaction(payload.emoji,user);embed=discord.Embed(title=f":robot: RAPPEL AUX JOUEURS :moyai:",description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.",color=COLOR_RED);await channel.send(embed=embed);await timeout(user,reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>")
                elif channel.id==CHANNEL_ID_VOTE and(not player.exists or not player.alive):
                        if not _J in[r.name for r in user.roles]:await msg.remove_reaction(payload.emoji,user);embed=discord.Embed(title=f":robot: Action interdite :moyai:",description=f":no_entry: Les aventuriers éliminés ne peuvent pas participer au vote.",color=COLOR_RED);await user.send(embed=embed)
                elif msg.channel.id==CHANNEL_ID_VOTE:
                        users=[]
                        for react in msg.reactions:users+=[user async for user in react.users()]
                        if users.count(user)>1:await msg.remove_reaction(payload.emoji,user)
@bot.command(pass_context=_A)
async def alliance(ctx,*args):
        if ctx.message.guild:await ctx.message.delete()
        player=Player(id=ctx.author.id)
        if not isinstance(ctx.channel,discord.channel.DMChannel):embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: Impossible d'effectuer l'action demandée : la commande *alliance* est disponible seulement en message privé avec le robot (ici).",color=COLOR_ORANGE);await ctx.author.send(embed=embed)
        elif not player.alive:embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: Impossible d'effectuer l'action demandée : les joueurs éliminés ne peuvent pas créer d'alliance.",color=COLOR_ORANGE);await ctx.author.send(embed=embed)
        else:general_guild=bot.get_guild(GUILD_ID);guild=discord.utils.get(general_guild.categories,id=CATEGORIE_ID_ALLIANCES);channel_name=args[0]if args[0]else'new_alliance';overwrites={general_guild.default_role:discord.PermissionOverwrite(read_messages=_D),ctx.author:discord.PermissionOverwrite(read_messages=_A)};new_text_channel=await guild.create_text_channel(channel_name,overwrites=overwrites);new_voice_channel=await guild.create_voice_channel(channel_name,overwrites=overwrites);new_alliance=NewAlliance();new_alliance.text_id=new_text_channel.id;new_alliance.voice_id=new_voice_channel.id;new_alliance.name=channel_name;new_alliance.creator=player._id;new_alliance.save();embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":white_check_mark: L'alliance {channel_name} a bien été créée : rendez-vous ici <#{new_text_channel.id}> pour y ajouter des joueurs.",color=COLOR_GREEN);await ctx.author.send(embed=embed)
@bot.command(pass_context=_A)
async def ajouter(ctx,*args):
        if ctx.message.guild:await ctx.message.delete()
        if len(args)==2:
                name=f"{args[0]} {args[1]}";player=Player(nickname=name)
                if player.id!=0:
                        if player.alive:user=bot.get_user(player.id);perms=ctx.channel.overwrites_for(user);perms.read_messages=_A;await ctx.channel.set_permissions(user,overwrite=perms);Alliance(text_id=ctx.channel.id).add_member(player._id);embed=discord.Embed(title=f":robot: Nouvelle alliance :moyai:",description=f":new: Vous avez été ajouté à l'alliance <#{ctx.channel.id}> par <@{ctx.author.id}> !",color=COLOR_GREEN);await user.send(embed=embed);embed=discord.Embed(title=f":robot: Nouveau membre :moyai:",description=f":new: <@{ctx.author.id}> a ajouté <@{player.id}> à l'alliance !",color=COLOR_GREEN);await ctx.send(embed=embed)
                        else:embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: Le joueur spécifié a été éliminé lors d'un vote, il est donc impossible de l'ajouter à une alliance.",color=COLOR_ORANGE);await ctx.send(embed=embed)
                else:embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: Le joueur spécifié est introuvable. Veuillez vérifier le fonctionnement de cette commande ici <#{CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER}>",color=COLOR_ORANGE);await ctx.send(embed=embed)
        else:embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: Le format requis n'est pas respecté. Veuillez vérifier le fonctionnement de cette commande ici <#{CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER}>",color=COLOR_ORANGE);await ctx.send(embed=embed)
@bot.command(pass_context=_A)
async def supprimer(ctx,member,*args):
        if ctx.message.guild:await ctx.message.delete()
        player=Player(id=member.id);perms=ctx.channel.overwrites_for(member);perms.read_messages=_D;await ctx.channel.set_permissions(member,overwrite=perms);Alliance(text_id=ctx.channel.id).remove_member(player._id);embed=discord.Embed(title=f":robot: Expulsion d'une alliance :moyai:",description=f":warning: Vous avez été supprimé de l'alliance *{ctx.channel.name}* par <@{ctx.author.id}> !",color=COLOR_ORANGE);await member.send(embed=embed);embed=discord.Embed(title=f":robot: Expulsion :moyai:",description=f":warning: <@{ctx.author.id}> a supprimé <@{player.id}> de l'alliance !",color=COLOR_ORANGE);await ctx.send(embed=embed)
@bot.command()
@commands.has_any_role(_B)
async def clear(ctx,amount=1):
        if ctx.message.guild:await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
@bot.command()
@commands.has_any_role(_B)
async def open_vote(ctx):await ctx.message.delete();await show_vote_msg()
@bot.command()
@commands.has_any_role(_B)
async def close_vote(ctx):await ctx.message.delete();await retrieval_of_results()
@bot.command(pass_context=_A)
@commands.has_any_role(_B)
async def mute(ctx,member,minutes=10,reason=_C):await ctx.message.delete();await timeout(member,author=ctx.author,minutes=minutes,reason=reason)
@bot.command(pass_context=_A)
@commands.has_any_role(_B)
async def unmute(ctx,member,minutes=10,reason=_C):await ctx.message.delete();await member.timeout(_C);embed=discord.Embed(title=f":robot: {member} Unmuted :moyai:",description=f"by **{ctx.author}**",color=COLOR_GREEN);await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
@bot.command(pass_context=_A)
@commands.has_any_role(_B)
async def send(ctx,channel,content,color='green'):await ctx.message.delete();embed=discord.Embed(title=f":robot: Information de {ctx.author.display_name} :moyai:",description=content,color=eval('COLOR_'+color.upper()));await channel.send(embed=embed)
@bot.command(pass_context=_A)
@commands.has_any_role(_B)
async def eliminer(ctx,member):await ctx.message.delete();eliminated=Player(id=member.id);players=Player(option=_K);players_list=players.list;embed=discord.Embed(title=f"**{eliminated.nickname}**",description=f"Le dernier éliminé a décidé de l'éliminer et sa sentence est irrévocable !",color=15548997);embed.set_author(name=_G,icon_url=_E);embed.set_thumbnail(url=_F);embed.add_field(name=f"Cet aventurier a reçu le vote du dernier éliminé suite à une égalité.",value=f"Il reste {len(players_list)-1} aventuriers en jeu.",inline=_A);channel=bot.get_channel(CHANNEL_ID_RESULTATS);await channel.send(embed=embed);guild=bot.get_guild(GUILD_ID);member=guild.get_member(eliminated.id);role=discord.utils.get(guild.roles,name=_H);new_role=discord.utils.get(guild.roles,name=_L);await member.remove_roles(role);await member.add_roles(new_role);eliminated.eliminate()
@bot.command(pass_context=_A)
@commands.has_any_role(_B)
async def start(ctx):await ctx.message.delete();Variables.start_game()
async def shedules_loop():schedules=Schedules()
class Schedules(commands.Cog):
        def __init__(self):
                self.action_performed=_C
                try:self.last_vote_date=datetime.datetime.strptime(Variables.get_last_vote_date(),_M)
                except:self.last_vote_date=_C
                if not self.last_vote_date:self.last_vote_date=datetime.datetime.now();bot.loop.create_task(self.send_message())
                self.verification.start()
        async def send_message(self):self.embed=discord.Embed(title=f":robot: Dernier vote introuvable :moyai:",description=f":warning: Impossible d'obtenir la date du dernier vote dans la base de donnée.\nDate appliquée : **{self.last_vote_date.strftime('%d/%m/%Y')}**",color=COLOR_ORANGE);await bot.get_channel(CHANNEL_ID_BOT).send(embed=self.embed)
        @tasks.loop(seconds=5)
        async def verification(self):
                self.time=datetime.datetime.now();self.hour=self.time.strftime('%H:%M')
                if self.hour=='18:00'and self.action_performed!=18:
                        if(self.time-self.last_vote_date).days>1 and Variables.get_state():self.action_performed=18;self.last_vote_date=self.time;Variables.set_last_vote_date(self.time.strftime(_M));await show_vote_msg()
                        else:self.action_performed=_C
                elif self.hour=='21:00'and self.action_performed==18:self.vote_in_progress=21;await retrieval_of_results()
async def timeout(member,**kwargs):author=kwargs.get('author','Denis Brogniart');reason_arg=kwargs.get('reason',_I);reason=reason_arg if reason_arg else _I;delta=datetime.timedelta(minutes=kwargs.get('minutes',10));await member.timeout(delta,reason=reason);embed=discord.Embed(title=f":robot: {member} Muted! :moyai:",description=f"by **{author}**\nbecause of **{reason}**\nfor **{delta}**",color=COLOR_RED);await bot.get_channel(CHANNEL_ID_BOT).send(embed=embed)
async def show_vote_msg():
        A='id';players=Player(option=_K);players_list=players.list
        if len(players_list)>2:embed=discord.Embed(title=f"Qui souhaitez-vous éliminer ce soir ?",description=f"Vous avez jusqu'à 21h ce soir pour choisir la personne que vous souhaitez éliminer en réagissant à ce message.",color=1086233);embed.set_author(name='Le conseil',icon_url=_E)
        else:
                embed=discord.Embed(title=f"Qui doit remporter cette saison ?",description=f"Vous avez jusqu'à 21h ce soir pour choisir la personne que remportera cette saison en réagissant à ce message.",color=1086233);embed.set_author(name='La Finale',icon_url=_E);guild=bot.get_guild(GUILD_ID);v_role=discord.utils.get(guild.roles,name=_J);f_role=discord.utils.get(guild.roles,name='Finaliste');voters=Player(option='eliminated');voters_list=voters.list
                for v in voters_list:await guild.get_member(v.get(A,0)).add_roles(v_role)
                category=discord.utils.get(guild.categories,name='Alliances')
                for f in players_list:
                        await guild.get_member(f.get(A,0)).add_roles(f_role)
                        for channel in category.channels:user=bot.get_user(f.get(A,0));perms=channel.overwrites_for(user);perms.read_messages=_D;await channel.set_permissions(user,overwrite=perms)     
        embed.set_thumbnail(url=_F);embed.set_footer(text='Choisissez la personne pour qui vous votez en cliquant sur une des cases ci-dessous.\nVous souhaitez savoir combien de personnes ont voté pour une personne ? Il suffit de soustraire 1 aux nombres inscrits ci-dessous. ');reactions=[]
        for(i,pl)in enumerate(players_list):embed.add_field(name=pl.get('nickname',_I),value=f"Choisir le logo {emojis[i]}",inline=_A);Player(id=pl.get(A)).set_letter(chr(i+65));reactions.append(emojis[i])
        channel=bot.get_channel(CHANNEL_ID_VOTE);msg=await channel.send(embed=embed);Variables.set_vote_msg_id(msg.id)
        for r in reactions:await msg.add_reaction(r)
async def retrieval_of_results():
        channel=bot.get_channel(CHANNEL_ID_VOTE);msg=await channel.fetch_message(Variables.get_vote_msg_id());reactions=msg.reactions;reactions_list={}
        for r in msg.reactions:
                async for u in r.users():
                        if u.id!=BOT_ID:
                                if u.id not in reactions_list:reactions_list[u.id]=[r.emoji]
                                elif r.emoji not in reactions_list[u.id]:reactions_list[u.id].append(r.emoji)
        await msg.delete();embed=discord.Embed(title=f":robot: Tricherie détectée :moyai:",description=f":no_entry: Vous avez voté pour plusieurs personnes en même temps.\nTous vos votes ont donc été annulés pour ce dernier vote.\nPar ailleurs, vous reçevez une sanction de type ban pendant 30 minutes.",color=COLOR_RED);embed.set_footer(text="Cette décision automatique n'est pas contestable. Vous pouvez néanmoins contacter un administrateur en MP pour signaler le problème.")
        for(uid,emojis)in reactions_list.items():
                if len(emojis)>1:
                        for react in reactions:
                                if react.emoji in emojis:react.count-=1
                        user=await bot.fetch_user(uid);await user.send(embed=embed);guild=bot.get_guild(GUILD_ID);member=guild.get_member(uid);await timeout(member,reason=f"Tentative de triche au vote.",minutes=30)
        max_reactions=[];max_count=0
        for reaction in reactions:
                if reaction.count>max_count:max_count=reaction.count;max_reactions=[reaction.emoji]
                elif reaction.count==max_count:max_reactions.append(reaction.emoji)
        if len(max_reactions)==1:eliminated=Player(letter=chr(emojis.index(max_reactions[0])+65));embed=discord.Embed(title=f"**{eliminated.nickname}**",description=f"Les aventuriers de la tribu ont décidé de l'éliminer et leur sentence est irrévocable !",color=15548997);embed.set_author(name=_G,icon_url=_E);embed.set_thumbnail(url=_F);embed.add_field(name=f"Cet aventurier a reçu {max_count-1} votes.",value=f"Il reste {len(reactions)-1} aventuriers en jeu.",inline=_A);channel=bot.get_channel(CHANNEL_ID_RESULTATS);await channel.send(embed=embed);guild=bot.get_guild(GUILD_ID);member=guild.get_member(eliminated.id);role=discord.utils.get(guild.roles,name=_H);new_role=discord.utils.get(guild.roles,name=_L);await member.remove_roles(role);await member.add_roles(new_role);eliminated.eliminate()     
        else:embed=discord.Embed(title=f"**Egalité**",description=f"Les aventuriers de la tribu n'ont pas sus se décider !",color=9807270);embed.set_author(name=_G,icon_url=_E);embed.set_thumbnail(url=_F);embed.add_field(name='La dernière personne éliminée va être contactée pas un administrateur afin de trancher entre les personnes atant actuellement à égalité.',value=f"Vous serez avertis via ce canal dès la décision prise et saisie.",inline=_A);channel=bot.get_channel(CHANNEL_ID_RESULTATS);await channel.send(embed=embed)
async def join(message):
        args=message.content.split(' ');player=message.author
        if Variables.get_state():embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: La partie a déjà débutée",color=COLOR_ORANGE);await player.send(embed=embed)     
        elif Player(id=player.id).exists:embed=discord.Embed(title=f":robot: Action inutile :moyai:",description=f":white_check_mark: Vous êtes déjà inscrit à cette partie.",color=COLOR_GREEN);embed.set_footer(text='En cas de problème, contacter un administrateur en MP.');await player.send(embed=embed)
        elif len(args)!=2 or len(args[0])==0 or len(args[1])!=1:embed=discord.Embed(title=f":robot: Action impossible :moyai:",description=f":warning: Vous devez renseigner votre prénom et initiale de nom comme suis : `Prénom N`\nDe plus, le prénom ne peut contenir d'espaces. Si besoin, utilisez des *-* .",color=COLOR_ORANGE);await player.send(embed=embed)
        else:
                nickname='{} {}'.format(args[0],args[1])
                try:await player.edit(nick=nickname)
                except:embed=discord.Embed(title=f":robot: Faible erreur :moyai:",description=f":warning: Une erreur est survenue lors du changement de votre nom sur le serveur : Veuillez contacter <@{USER_ID_ADMIN}> pour qu'il effectue la modification manuellement.\nPas d'inquiétude, le processus d'inscription continue normalement, cela n'auras aucun impact.",color=COLOR_ORANGE);await player.send(embed=embed)
                new_player=NewPlayer();new_player.id=player.id;new_player.nickname=nickname;new_player.save();role=discord.utils.get(message.guild.roles,name=_H);await player.add_roles(role);embed=discord.Embed(title=f":robot: Bienvenue ! :moyai:",description=f":white_check_mark: Bienvenue dans cette saison de Koh Lanta IRL !\nTon compte a été paramétré avec succès, nous te laissons découvrir les différents salons et les différentes actions que tu peux effectuer sur ce serveur.\nA très vite !",color=COLOR_GREEN);await player.send(embed=embed);embed=discord.Embed(title=f":confetti_ball: On souhaite la bienvenue à **{nickname}** qui participera à la prochaine saison de Koh Lanta IRL !:confetti_ball:",color=COLOR_GREEN);await bot.get_channel(CHANNEL_ID_GENERAL).send(embed=embed)
async def set_inscription_infos():embed=discord.Embed(title=f"Vous souhaitez nous rejoindre ?",description=f"Vous pouvez dès à présent vous inscrire à la prochaine saison de KohLanta IRL !",color=1086233);embed.set_author(name='Inscription',icon_url='https://cdn.discordapp.com/avatars/1139673903678095400/fe3974836708aab020a743b2700e87e4.webp?size=100');embed.set_thumbnail(url='https://photos.tf1.fr/1200/720/vignette-16-9-4d6adf-748cc7-0@1x.webp');embed.add_field(name="Entrez votre prénom et l'initale de votre nom dans le champ ci-dessous.",value='Exemple : Arthur D',inline=_D);embed.add_field(name='Le prénom ne doit pas contenir d\'espace ou de caractère spécial autre que "-".',value='Vous avez un prénom composé ? Remplacez les espaces par un caractère "-".',inline=_D);embed.set_footer(text=f"Vous rencontrez un problème ? Contactez dès que possible un administrateur.");channel=bot.get_channel(CHANNEL_ID_INSCRIPTION);await channel.send(embed=embed)
async def send_missing_permission_msg(ctx):0
bot.run(TOKEN)