import datetime
import typing

import discord

from config.values import (BOT_ID, CATEGORIE_ID_ALLIANCES,
                           CHANNEL_ID_RESULTATS, CHANNEL_ID_VOTE, COLOR_GREEN,
                           COLOR_RED, EMOJIS_LIST, GUILD_ID)
from database.game import Game
from database.player import Player, PlayerList
from database.votelog import VoteLog, VoteLogList
from utils.bot import bot
from utils.log import get_logger
from utils.pdf import generate as pdfGenerate
from utils.punishments import timeout

logger = get_logger(__name__)

select_options = []


async def open(interaction: discord.Interaction = None):
    """Open the vote."""

    logger.info(f'vote opening > start | interaction: {interaction}')
    guild = bot.get_guild(GUILD_ID)
    players = PlayerList(alive=True)
    if len(players.objects) > 2:
        embed = discord.Embed(
            title='Qui souhaitez-vous éliminer ce soir ?',
            description="Vous avez jusqu'à 21h ce soir pour choisir la personne que vous souhaitez éliminer en réagissant à ce message.",
            color=0x109319,
        )
        embed.set_author(
            name='Le conseil',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
    else:
        embed = discord.Embed(
            title='Qui doit remporter cette saison ?',
            description="Vous avez jusqu'à 23h59 ce soir pour choisir la personne que remportera cette saison en réagissant à ce message.",
            color=0x109319,
        )
        embed.set_author(
            name='La Finale',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        v_role = discord.utils.get(
            guild.roles, name='Votant Final'
        )  # Récupération du role 'Votant final'
        f_role = discord.utils.get(
            guild.roles, name='Finaliste'
        )  # Récupération du role 'Finaliste
        voters = PlayerList(alive=False)
        voters_list = voters.objects
        for v in voters_list:
            await guild.get_member(v.object.id).add_roles(
                v_role
            )  # Assignation du nouveau role
        category = discord.utils.get(guild.categories, id=CATEGORIE_ID_ALLIANCES)
        for f in players.objects:
            await guild.get_member(int(f.object.id)).add_roles(
                f_role
            )  # Assignation du nouveau role
            for channel in category.channels:
                user = bot.get_user(int(f.object.id))
                perms = channel.overwrites_for(user)
                perms.read_messages = False
                await channel.set_permissions(user, overwrite=perms)
        Game.start_last_vote()
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    embed.set_footer(
        text='Choisissez la personne pour qui vous votez en cliquant sur une des cases ci-dessous.\nVous souhaitez savoir combien de personnes ont voté pour une personne ? Il suffit de soustraire 1 aux nombres inscrits ci-dessous. '
    )
    reactions = []
    for i, pl in enumerate(players.objects):
        embed.add_field(
            name=pl.object.nickname,
            value=f'Choisir le logo {EMOJIS_LIST[i]}',
            inline=True,
        )
        pl.object.letter = chr(i + 65)
        pl.save()
        reactions.append(EMOJIS_LIST[i])
    channel = bot.get_channel(CHANNEL_ID_VOTE)
    everyone_role = discord.utils.get(
        guild.roles, name='@everyone'
    )
    await channel.set_permissions(everyone_role, read_messages=None)
    msg = await channel.send(embed=embed)
    Game.vote_msg_id = msg.id
    for r in reactions:
        await msg.add_reaction(r)
    if interaction:
        embed = discord.Embed(
            title=':robot: Le vote est ouvert :moyai:', color=COLOR_GREEN
        )
        await interaction.followup.send(embed=embed)
    logger.info(f'vote opening > OK | interaction: {interaction}')


async def arrange_votes_for_deal_with_cheaters(reactions: list) -> dict:
    """Arrange the votes in a dict for the deal_with_cheaters function."""

    logger.info('arrange vote for deal with cheaters > start')
    reactions_dict = {}
    for r in reactions:
        async for u in r.users():
            if u.id != BOT_ID:
                if u.id not in reactions_dict:
                    reactions_dict[u.id] = [r.emoji]
                elif r.emoji not in reactions_dict[u.id]:
                    reactions_dict[u.id].append(r.emoji)
    logger.info('arrange vote for deal with cheaters > OK')
    return reactions_dict


async def arrange_votes_for_votelog(reactions: list) -> list:
    """Arrange the votes in a list for the VoteLog."""

    logger.info('arrange vote for votelog > start')
    reactions_list = []
    for r in reactions:
        async for u in r.users():
            if u.id != BOT_ID:
                reactions_list.append(
                    {
                        'voter': Player(id=u.id).object._id,
                        'for': Player(letter=chr(EMOJIS_LIST.index(r.emoji) + 65)).object._id
                    }
                )

    logger.info('arrange vote for votelog > OK')
    return reactions_list


async def deal_with_cheaters(reactions: list) -> int:
    """Deal with the cheaters."""

    logger.info('deal with cheaters > start')
    cheaters_number = 0
    embed = discord.Embed(
        title=':robot: Tricherie détectée :moyai:',
        description=':no_entry: Vous avez voté pour plusieurs personnes en même temps.\nTous vos votes ont donc été annulés pour ce dernier vote.\nPar ailleurs, vous reçevez une sanction de type ban pendant 30 minutes.',
        color=COLOR_RED,
    )
    embed.set_footer(
        text="Cette décision automatique n'est pas contestable. Vous pouvez néanmoins contacter un administrateur en MP pour signaler un éventuel problème."
    )
    reactions_dict = await arrange_votes_for_deal_with_cheaters(reactions)
    for uid, emojis in reactions_dict.items():
        if len(emojis) > 1:
            for react in reactions:
                if react.emoji in emojis:
                    react.count -= 1
            user = await bot.fetch_user(uid)
            await user.send(embed=embed)
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(uid)
            await timeout(member, reason='Tentative de triche au vote.', minutes=30)
            del reactions_dict[uid]
            cheaters_number += 1
    logger.info(f'deal with cheaters > OK | cheaters number: {cheaters_number}')
    return cheaters_number


async def count_votes(reactions: list) -> typing.Union[list, int, bool, bool]:
    """Count the votes."""

    logger.info('count votes > start')
    max_reactions = []
    max_count = 0
    for reaction in reactions:
        if reaction.count > max_count:
            max_count = reaction.count
            max_reactions = [reaction.emoji]
        elif reaction.count == max_count:
            max_reactions.append(reaction.emoji)

    it_is_the_final = len(reactions) == 2
    no_tied_players = len(max_reactions) == 1
    logger.info(
        f'count votes > OK | it_is_the_final: {it_is_the_final} | tied_players: {no_tied_players == False}'
    )
    return max_reactions, max_count, it_is_the_final, no_tied_players


async def eliminate(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: typing.Literal['After equality', 'Other reason'],
) -> None:
    """Eliminate a player."""

    logger.info(f'eliminate > start | member: {member} | reason: {reason}')
    eliminated = Player(id=member.id)
    players = PlayerList(alive=True)
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    if reason == 'After equality':
        public_embed = discord.Embed(
            title='**{eliminated.object.nickname}**',
            description="Le dernier éliminé a décidé de l'éliminer et sa sentence est irrévocable !",
            color=15548997,
        )
        public_embed.set_author(
            name='Résultat du conseil',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        public_embed.set_thumbnail(
            url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
        )
        public_embed.add_field(
            name='Cet aventurier a reçu le vote du dernier éliminé suite à une égalité.',
            value=f'Il reste {len(players.objects)-1} aventuriers en jeu.',
            inline=True,
        )
        dm_embed = discord.Embed(
            title='**Tu quittes la tribu ce soir** (cheh)',
            description="Les aventuriers ont décidé de t'éliminer et leur sentence est irrévocable !",
            color=15548997,
        )
        max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        dm_embed.set_author(
            name='Résultat du conseil',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        dm_embed.set_thumbnail(
            url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
        )
        dm_embed.add_field(
            name='Tu as reçu le votes du dernier éliminé',
            value=f"Plus d'infos ici: <#{CHANNEL_ID_RESULTATS}>.",
            inline=False,
        )
        dm_embed.add_field(
            name='Tu souhaites exprimer une dernière volonté ? Envoi moi la commande /dv !',
            value=f"Exemple : `/dv \'Vous n'auriez pas dû m'éliminer...\'`\nEnvoi moi simplement un message sous cette forme.\nTu peux utiliser cette commande jusqu'à la date suivante : {max_date.strftime('%d/%m/%Y %H:%M:%S')}",
        )
        last_vote_log = VoteLog(last=True)
        last_vote_log.update_eliminated(Player(id=member.id).object)
        file_path = pdfGenerate(last_vote_log.number)
        file = discord.File(file_path)
        await channel.send(embed=public_embed, file=file)
    else:
        public_embed = discord.Embed(
            title=f'**{eliminated.nickname}**',
            description=f"<@{interaction.user.id}> a décidé de l'éliminer et sa sentence est irrévocable !",
            color=15548997,
        )
        public_embed.set_author(
            name="Décision d'un administrateur",
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        public_embed.set_thumbnail(
            url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
        )
        public_embed.add_field(
            name='Cet aventurier a été éliminé par un administrateur.',
            value=f'Il reste {len(players.objects)-1} aventuriers en jeu.',
            inline=True,
        )
        dm_embed = discord.Embed(
            title='**Tu quittes la tribu **',
            description=f"<@{interaction.user.id}> a décidé de t'éliminer et sa sentence est irrévocable !\nTu es en droit de le contacter en DM.",
            color=15548997,
        )
        dm_embed.set_author(
            name="Décision d'un administrateur",
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        dm_embed.set_thumbnail(
            url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
        )
        dm_embed.add_field(
            name="Pas d'expression de dernière volonté",
            value="Etant donné les règles du jeu, tu ne disposes pas d'un droit d'expression d'une dernière volonté.",
        )
        embed = discord.Embed(
            title=':robot: Joueur éliminé :moyai:',
            description=f'player : <@{member.id}>',
            color=COLOR_GREEN,
        )
        await interaction.followup.send(embed=embed)
        await channel.send(embed=public_embed)
    await member.send(embed=dm_embed)
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name='Joueur')
    new_role = discord.utils.get(guild.roles, name='Eliminé')
    await member.remove_roles(role)
    await member.add_roles(new_role)
    eliminated.eliminate()
    logger.info(f'eliminate > OK | member: {member} | reason: {reason}')


async def resurrect(interaction: discord.Interaction, member: discord.Member) -> None:
    """Resurrect a player."""

    logger.info(f'resurrect > start | member: {member}')
    resurrected = Player(id=member.id)
    dm_embed = discord.Embed(
        title='**Tu réintègres la tribu **',
        description=f'<@{interaction.user.id}> a décidé de te réintégrer et tu lui dois beaucoup !',
        color=COLOR_GREEN,
    )
    dm_embed.set_author(
        name="Décision d'un administrateur",
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    dm_embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    await member.send(embed=dm_embed)
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name='Eliminé')
    new_role = discord.utils.get(guild.roles, name='Joueur')
    await member.remove_roles(role)
    await member.add_roles(new_role)
    resurrected.resurrect()
    embed = discord.Embed(
        title=':robot: Joueur réssuscité :moyai:',
        description=f'player : <@{member.id}>',
        color=COLOR_GREEN,
    )
    await interaction.followup.send(embed=embed)
    logger.info(f'resurrect > OK | member: {member}')


async def set_finalist(interaction: discord.Interaction, member: discord.Member):
    """Set a player as finalist."""

    logger.info(f'set finalist > start | member: {member}')
    dm_embed = discord.Embed(
        title='**Tu est élevé au rang de finaliste**',
        description=f'<@{interaction.user.id}> a décidé de te désigner comme finaliste et tu lui dois beaucoup !',
        color=COLOR_GREEN,
    )
    dm_embed.set_author(
        name="Décision d'un administrateur",
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    dm_embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    await member.send(embed=dm_embed)
    guild = bot.get_guild(GUILD_ID)
    new_role = discord.utils.get(guild.roles, name='Finaliste')
    await member.add_roles(new_role)
    embed = discord.Embed(
        title=':robot: Joueur défini comme finaliste :moyai:',
        description=f'player : <@{member.id}>',
        color=COLOR_GREEN,
    )
    await interaction.followup.send(embed=embed)
    logger.info(f'set finalist > OK | member: {member}')


async def check_if_last_eliminate_is_saved():
    """Check if the last eliminate is saved."""

    logger.info('check if last eliminate is saved > start')
    last_vote_log = VoteLog(last=True)
    if last_vote_log.eliminated == [] and last_vote_log._id:
        tied_players = last_vote_log.tied_players
        public_embed = discord.Embed(
            title=f"**{', '.join([el.nickname for el in tied_players])}**",
            description="Le dernier éliminé n'a pas choisi de joueur à sauver et les condamne tous !",
            color=15548997,
        )
        public_embed.set_author(
            name='Résultat du conseil',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        public_embed.set_thumbnail(
            url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
        )
        public_embed.add_field(
            name="Le dernier éliminé n'ayant pas fait son choix dans le temps imparti, tous les joueurs à égalité ont été éliminés.",
            value=f'Il reste {len(PlayerList(alive=True).objects)-1} aventuriers en jeu.',
            inline=True,
        )
        dm_embed = discord.Embed(
            title='**Tu quittes la tribu ce soir** (cheh)',
            description="Le dernier éliminé n'ayant pas fait son choix dans le temps imparti, tous les joueurs à égalité ont été éliminés.",
            color=15548997,
        )
        max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        dm_embed.set_author(
            name='Résultat du conseil',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        dm_embed.set_thumbnail(
            url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
        )
        dm_embed.add_field(
            name="Tu n'as pas été sauvé par le dernier éliminé !",
            value=f"Plus d'infos ici: <#{CHANNEL_ID_RESULTATS}>.",
            inline=False,
        )
        dm_embed.add_field(
            name='Tu souhaites exprimer une dernière volonté ? Envoi moi la commande /dv !',
            value=f"Exemple : `/dv \'Vous n'auriez pas dû m'éliminer...\'`\nEnvoi moi simplement un message sous cette forme.\nTu peux utiliser cette commande jusqu'à la date suivante : {max_date.strftime('%d/%m/%Y %H:%M:%S')}",
        )
        last_vote_log.update_eliminated(tied_players)
        file_path = pdfGenerate(last_vote_log.number)
        file = discord.File(file_path)
        channel = bot.get_channel(CHANNEL_ID_RESULTATS)
        await channel.send(embed=public_embed, file=file)
        guild = bot.get_guild(GUILD_ID)
        role = discord.utils.get(guild.roles, name='Joueur')
        new_role = discord.utils.get(guild.roles, name='Eliminé')
        for el in tied_players:
            member = guild.get_member(el.id)
            await member.remove_roles(role)
            await member.add_roles(new_role)
            await member.send(ember=dm_embed)
            el.eliminate()
    logger.info('check if last eliminate is saved > OK')


async def reset_votes() -> None:
    """Reset the votes."""

    logger.info('reset votes > start')
    for v in VoteLogList().objects:
        v.delete()
    vote_channel = bot.get_channel(CHANNEL_ID_VOTE)
    await vote_channel.purge()
    results_channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await results_channel.purge()
    logger.info('reset votes > OK')
