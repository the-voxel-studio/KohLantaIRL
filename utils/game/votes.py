import discord
from utils.models import Player, Variables
from utils.bot import bot
from utils.punishments import timeout
from config.values import GUILD_ID, EMOJIS_LIST, CHANNEL_ID_VOTE, COLOR_GREEN, COLOR_RED, BOT_ID, CHANNEL_ID_RESULTATS

async def open(interaction: discord.Interaction = None):# TODO add logs
    players = Player(option="living")
    players_list = players.list
    if len(players_list) > 2:
        embed = discord.Embed(title=f"Qui souhaitez-vous éliminer ce soir ?",description=f"Vous avez jusqu'à 21h ce soir pour choisir la personne que vous souhaitez éliminer en réagissant à ce message.",color=0x109319)
        embed.set_author(name="Le conseil",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
    else:
        embed = discord.Embed(title=f"Qui doit remporter cette saison ?",description=f"Vous avez jusqu'à 23h59 ce soir pour choisir la personne que remportera cette saison en réagissant à ce message.",color=0x109319)
        embed.set_author(name="La Finale",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
        guild = bot.get_guild(GUILD_ID)
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
                user = bot.get_user(f.get("id",0))
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
    channel = bot.get_channel(CHANNEL_ID_VOTE)
    msg = await channel.send(embed=embed)
    Variables.set_vote_msg_id(msg.id)
    for r in reactions:
        await msg.add_reaction(r)
    if interaction:
        embed=discord.Embed(title=f":robot: Le vote est ouvert :moyai:", color=COLOR_GREEN)
        await interaction.followup.send(embed=embed)

async def close(interaction: discord.Interaction = None):# TODO add logs
    channel = bot.get_channel(CHANNEL_ID_VOTE)
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
            user = await bot.fetch_user(uid)
            await user.send(embed=embed)
            guild = bot.get_guild(GUILD_ID)
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
        channel = bot.get_channel(CHANNEL_ID_RESULTATS)
        await channel.send(embed=embed)
        guild = bot.get_guild(GUILD_ID)
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
        channel = bot.get_channel(CHANNEL_ID_RESULTATS)
        await channel.send(embed=embed)
    if interaction : 
        embed=discord.Embed(title=f":robot: Le vote est clos :moyai:", color=COLOR_GREEN)
        await interaction.followup.send(embed=embed)
    # except:
    #     pass