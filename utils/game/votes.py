import typing

import discord

from config.values import (
    BOT_ID,
    CHANNEL_ID_RESULTATS,
    CHANNEL_ID_VOTE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_ORANGE,
    EMOJIS_LIST,
    GUILD_ID,
    CATEGORIE_ID_ALLIANCES,
)
from utils.bot import bot
from utils.log import get_logger
from utils.models import Player, Variables, NewVoteLog, VoteLog, get_council_number
from utils.punishments import timeout
from utils.game.players import reset_roles
from utils.pdf import generate as pdfGenerate
from utils.game.immuniteCollar import remove_potential_immune_player
from utils.game.alliances import purge_alliances
import datetime

logger = get_logger(__name__)

select_options = []


async def open(interaction: discord.Interaction = None):
    logger.info(f'vote opening > start | interaction: {interaction}')
    players = Player(option='living')
    players_list = players.list
    if len(players_list) > 2:
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
        guild = bot.get_guild(GUILD_ID)
        v_role = discord.utils.get(
            guild.roles, name='Votant Final'
        )  # Récupération du role 'Votant final'
        f_role = discord.utils.get(
            guild.roles, name='Finaliste'
        )  # Récupération du role 'Finaliste'
        voters = Player(option='eliminated')
        voters_list = voters.list
        for v in voters_list:
            await guild.get_member(v.get('id', 0)).add_roles(
                v_role
            )  # Assignation du nouveau role
        category = discord.utils.get(guild.categories, id=CATEGORIE_ID_ALLIANCES)
        for f in players_list:
            await guild.get_member(int(f.get('id', 0))).add_roles(
                f_role
            )  # Assignation du nouveau role
            for channel in category.channels:
                user = bot.get_user(int(f.get('id', 0)))
                perms = channel.overwrites_for(user)
                perms.read_messages = False
                await channel.set_permissions(user, overwrite=perms)
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    embed.set_footer(
        text='Choisissez la personne pour qui vous votez en cliquant sur une des cases ci-dessous.\nVous souhaitez savoir combien de personnes ont voté pour une personne ? Il suffit de soustraire 1 aux nombres inscrits ci-dessous. '
    )
    reactions = []
    for i, pl in enumerate(players_list):
        embed.add_field(
            name=pl.get('nickname', 'unknown'),
            value=f'Choisir le logo {EMOJIS_LIST[i]}',
            inline=True,
        )
        Player(id=pl.get('id')).set_letter(chr(i + 65))
        reactions.append(EMOJIS_LIST[i])
    channel = bot.get_channel(CHANNEL_ID_VOTE)
    msg = await channel.send(embed=embed)
    Variables.set_vote_msg_id(msg.id)
    Variables.start_last_vote()
    for r in reactions:
        await msg.add_reaction(r)
    if interaction:
        embed = discord.Embed(
            title=':robot: Le vote est ouvert :moyai:', color=COLOR_GREEN
        )
        await interaction.followup.send(embed=embed)
    logger.info(f'vote opening > OK | interaction: {interaction}')


class EqualityView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.council_number = get_council_number()
        self.select = discord.ui.Select(
            placeholder='Choisis une personne à éliminer !',
            min_values=1,
            max_values=1,
            options=select_options,
            custom_id='tied_players_selection',
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)
        logger.info(f'EqualityView __init__ > OK | select_options: {select_options}')

    async def select_callback(self, interaction):
        logger.info(f'EqualityView select_callback > start | user: {interaction.user} (id: {interaction.user.id})')
        await interaction.response.defer()
        self.select.disabled = True
        await interaction.message.edit(view=self)
        now_date = datetime.datetime.now()
        last_vote_date = datetime.datetime.strptime(
            VoteLog(last=True).date, '%d/%m/%Y %H:%M:%S'
        )
        time_delta = now_date - last_vote_date
        in_time = time_delta < datetime.timedelta(hours=17)  # 14h the day after the tie vote
        if in_time:
            eliminated_nickname = interaction.data['values'][0]
            embed = discord.Embed(
                title=f'**Tu as éliminé {eliminated_nickname} !**', color=9807270
            )
            embed.set_author(
                name=f'Egalité au conseil n°{self.council_number} !',
                icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
            )
            embed.set_thumbnail(
                url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
            )
            guild = bot.get_guild(GUILD_ID)
            member = discord.utils.get(guild.members, nick=eliminated_nickname)
            await eliminate(interaction, member, 'After equality')
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title=':robot: Trop tard ! :moyai:',
                description=':no_entry: Le selection est maintenant fermée, vous avez dépacé le délais imparti. Par votre faute, les deux joueurs ont dors et déjà été éliminés !',
                color=COLOR_ORANGE,
            )
            embed.set_footer(
                text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
            )
            embed.set_image(url='https://media.tenor.com/CCLg0rGFVHEAAAAC/ah-denis.gif')
            await interaction.followup.send(embed=embed)
        logger.info(f'EqualityView select_callback > OK | user: {interaction.user} (id: {interaction.user.id}) | in_time: {in_time}')


async def arrange_votes(reactions: list) -> dict:
    logger.info('arrange vote > start')
    reactions_list = {}
    for r in reactions:
        async for u in r.users():
            if u.id != BOT_ID:
                if u.id not in reactions_list:
                    reactions_list[u.id] = [r.emoji]
                elif r.emoji not in reactions_list[u.id]:
                    reactions_list[u.id].append(r.emoji)
    logger.info('arrange vote > OK')
    return reactions_list


async def deal_with_cheaters(reactions_list: dict, reactions: list) -> int:
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
    for uid, emojis in reactions_list.items():
        if len(emojis) > 1:
            for react in reactions:
                if react.emoji in emojis:
                    react.count -= 1
            user = await bot.fetch_user(uid)
            await user.send(embed=embed)
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(uid)
            await timeout(member, reason='Tentative de triche au vote.', minutes=30)
            del reactions_list[uid]
            cheaters_number += 1
    logger.info(f'deal with cheaters > OK | cheaters number: {cheaters_number}')
    return cheaters_number


async def count_votes(reactions: list) -> typing.Union[list, int, bool, bool]:
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


async def close_final_vote(
    max_reactions, reactions_list, cheaters_number, max_count
) -> None:
    logger.info('close_final_vote > start ')
    logger.info('EqualityView select_callback > start | max_rea')
    winner = Player(letter=chr(EMOJIS_LIST.index(max_reactions[0]) + 65))
    new_vote_log = NewVoteLog(
        votes=reactions_list, eliminated=[winner], cheaters_number=cheaters_number
    )
    new_vote_log.save()
    embed = discord.Embed(
        title=f'**{winner.nickname}** remporte la partie !',
        description="Les aventuriers de la tribu ont décidé de l'élire en tant que vainqueur de cette saison et leur sentence est irrévocable !",
        color=COLOR_GREEN,
    )
    embed.set_author(
        name='Résultat du conseil final',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    embed.add_field(
        name=f'Cet aventurier a reçu {max_count-1} votes.',
        value='La partie prend donc fin maintenant',
        inline=True,
    )
    file_path = pdfGenerate(new_vote_log.number, final=True)
    file = discord.File(file_path)
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed, file=file)
    embed = discord.Embed(
        title='**Tu remportes la saison ce soir !**',
        description="Les aventuriers de la tribu ont décidé de t'élire en tant que vainqueur de cette saison et leur sentence est irrévocable !",
        color=15548997,
    )
    embed.set_author(
        name='Résultat du conseil final',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    embed.add_field(
        name=f'Tu as reçu {max_count-1} votes.',
        value=f"Plus d'infos ici: <#{CHANNEL_ID_RESULTATS}>.",
        inline=False,
    )
    embed.set_image(url='https://media.tenor.com/b4GVF1aUlgIAAAAC/chirac-victoire.gif')
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(winner.id)
    await member.send(embed=embed)
    await reset_roles('Joueur', 'Eliminé', 'Finaliste', 'Votant Final')
    await purge_alliances()
    logger.info('close_final_vote > OK ')


async def close_normal(
    max_reactions, reactions_list, cheaters_number, max_count, reactions
) -> None:
    logger.info('close_normal > start ')
    eliminated = Player(letter=chr(EMOJIS_LIST.index(max_reactions[0]) + 65))
    new_vote_log = NewVoteLog(
        votes=reactions_list,
        eliminated=[eliminated],
        cheaters_number=cheaters_number,
    )
    new_vote_log.save()
    nb_remaining_players = len(reactions) - 1
    embed = discord.Embed(
        title=f'**{eliminated.nickname}**',
        description="Les aventuriers de la tribu ont décidé de l'éliminer et leur sentence est irrévocable !",
        color=15548997,
    )
    embed.set_author(
        name=f'Résultat du conseil n°{get_council_number()}',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    value = (
        f'Il reste {nb_remaining_players} aventuriers en jeu.'
        if nb_remaining_players != 1
        else ''
    )
    embed.add_field(
        name=f'Cet aventurier a reçu {max_count-1} votes.',
        value=value,
        inline=True,
    )
    file_path = pdfGenerate(new_vote_log.number)
    file = discord.File(file_path)
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed, file=file)
    max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
        hour=21, minute=0, second=0, microsecond=0
    )
    embed = discord.Embed(
        title='**Tu quittes la tribu ce soir** (cheh)',
        description="Les aventuriers ont décidé de t'éliminer et leur sentence est irrévocable !",
        color=15548997,
    )
    embed.set_author(
        name='Résultat du conseil',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    embed.add_field(
        name=f'Tu as reçu {max_count-1} votes.',
        value=f"Plus d'infos ici: <#{CHANNEL_ID_RESULTATS}>.",
        inline=False,
    )
    embed.add_field(
        name='Tu souhaites exprimer une dernière volonté ? Envoi moi la commande /dv !',
        value=f"Exemple : `/dv \'Vous n'auriez pas dû m'éliminer...\'`\nEnvoi moi simplement un message sous cette forme.\nTu peux utiliser cette commande jusqu'à la date suivante : {max_date.strftime('%d/%m/%Y %H:%M:%S')}",
    )
    embed.set_image(url='https://media.tenor.com/dvnQzSrXuGQAAAAC/sam-koh-lanta.gif')
    guild = bot.get_guild(GUILD_ID)
    logger.warning(f'eliminated: {eliminated}')
    member = guild.get_member(eliminated.id)
    await member.send(embed=embed)
    role = discord.utils.get(guild.roles, name='Joueur')
    new_role = discord.utils.get(guild.roles, name='Eliminé')
    await member.remove_roles(role)
    await member.add_roles(new_role)
    eliminated.eliminate()
    if nb_remaining_players == 1:
        Variables.wait_for_last_vote()
    logger.info('close_normal > OK ')


async def close_normal_equality(
    reactions_list, cheaters_number, council_number, it_is_the_final, tied_players
) -> None:
    global select_options
    logger.info('close_normal_equality > start ')
    NewVoteLog(
        votes=reactions_list, cheaters_number=cheaters_number, tied_players=tied_players
    ).save()
    embed = discord.Embed(
        title='**Egalité**',
        description="Les aventuriers de la tribu n'ont pas sus se décider !",
        color=9807270,
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    if it_is_the_final:
        vote_denomination = 'final'
        vote_chooser1 = 'Le vainqueur de la saison précédente'
        vote_chooser2 = 'dernier vainqueur en date'
        vote_chooser_id = Variables.get_last_winner_id()
    else:
        vote_denomination = f'n°{council_number}'
        vote_chooser1 = 'La dernière personne éliminée'
        vote_chooser2 = 'dernière personne éliminée'
        try:
            vote_chooser_id = VoteLog(last=-1).eliminated[0].id
        except IndexError:
            vote_chooser_id = VoteLog(last=-2).eliminated[0].id

    embed.set_author(
        name=f'Résultat du conseil {vote_denomination}',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.add_field(
        name=f'{vote_chooser1} doit maintenant trancher entre les personnes étant actuellement à égalité.',
        value='Vous serez avertis via ce canal dès la décision prise et saisie.',
        inline=True,
    )
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed)
    max_date = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )
    embed = discord.Embed(
        title='**A toi de choisir !**',
        description=f"En tant que {vote_chooser2}, tu dois décider de l'issue de ce vote {vote_denomination} !\nTu dois choisir ci-dessous entre les personnes arrivées à égalité.\nAttention, toute sélection est définitive.\nTu dois faire ton choix avant la date suivante : {max_date.strftime('%d/%m/%Y %H:%M:%S')}",
        color=9807270,
    )
    embed.set_author(
        name=f'Egalité au conseil {vote_denomination} !',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    chooser = discord.utils.get(bot.get_all_members(), id=vote_chooser_id)
    select_options = [
        discord.SelectOption(label=p.nickname, description=f'Eliminer {p.nickname}')
        for p in tied_players
    ]
    await chooser.send(embed=embed, view=EqualityView())
    logger.info('close_normal_equality > OK ')


async def close_first_vote_equality(
    reactions_list, cheaters_number, tied_players
) -> None:
    logger.info('close_first_vote_equality > start ')
    new_vote_log = NewVoteLog(
        votes=reactions_list,
        eliminated=tied_players,
        cheaters_number=cheaters_number,
        tied_players=tied_players,
    )
    new_vote_log.save()
    embed = discord.Embed(
        title='**Egalité**',
        description="Les aventuriers de la tribu n'ont pas sus se décider !",
        color=9807270,
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    embed.set_author(
        name='Résultat du conseil n°1',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.add_field(
        name='En vertue des règles du jeu, tous les joueurs à égalité ont donc été éliminés.',
        value='Pour les futures égalités, ce sera au dernier éliminé en date de choisir entre les personne à égalité.',
    )
    file_path = pdfGenerate(new_vote_log.number)
    file = discord.File(file_path)
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed, file=file)
    dm_embed = discord.Embed(
        title='**Tu quittes la tribu ce soir** (cheh)',
        description='Etant à égalité lors du premier vote, tu es éliminé dès ce soir.',
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
        name="Tu n'as pas sû te démarquer, et le premier conseil est le plus rude !",
        value=f"Plus d'infos ici: <#{CHANNEL_ID_RESULTATS}>.",
        inline=False,
    )
    dm_embed.add_field(
        name='Tu souhaites exprimer une dernière volonté ? Envoi moi la commande /dv !',
        value=f"Exemple : `/dv \'Vous n'auriez pas dû m'éliminer...\'`\nEnvoi moi simplement un message sous cette forme.\nTu peux utiliser cette commande jusqu'à la date suivante : {max_date.strftime('%d/%m/%Y %H:%M:%S')}",
    )
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name='Joueur')
    new_role = discord.utils.get(guild.roles, name='Eliminé')
    for el in tied_players:
        member = guild.get_member(el.id)
        await member.remove_roles(role)
        await member.add_roles(new_role)
        await member.send(embed=dm_embed)
        el.eliminate()
    logger.info('close_first_vote_equality > OK ')


async def close_without_eliminated(
    max_reactions, reactions_list, cheaters_number, immune, reactions
) -> None:
    logger.info('close_without_eliminated > start ')
    new_vote_log = NewVoteLog(
        votes=reactions_list,
        eliminated=[],
        cheaters_number=cheaters_number,
    )
    new_vote_log.save()
    nb_remaining_players = len(reactions) - 1
    embed = discord.Embed(
        title='**Aucun joueur éliminé**',
        description="Suite aux résultat du vote, personne n'a été éliminé !",
        color=15548997,
    )
    embed.set_author(
        name=f'Résultat du conseil n°{get_council_number()}',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp'
    )
    value = (
        f'Il reste {nb_remaining_players} aventuriers en jeu.'
        if nb_remaining_players != 1
        else ''
    )
    embed.add_field(
        name="Un collier d'immunité a été utilisé.",
        value=value,
        inline=True,
    )
    file_path = pdfGenerate(new_vote_log.number)
    file = discord.File(file_path)
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed, file=file)
    logger.info('close_without_eliminated > OK ')


async def close(interaction: discord.Interaction = None) -> None:
    # [ ] ? save immune persons in VoteLog
    logger.info('vote closing > start')
    channel = bot.get_channel(CHANNEL_ID_VOTE)
    msg = await channel.fetch_message(Variables.get_vote_msg_id())
    reactions = msg.reactions
    reactions_list = await arrange_votes(reactions)
    await msg.delete()
    Variables.set_vote_msg_id(0)
    cheaters_number = await deal_with_cheaters(reactions_list, reactions)
    max_reactions, max_count, it_is_the_final, there_is_no_equality = await count_votes(
        reactions
    )
    if not it_is_the_final:
        max_reactions, immune = await remove_potential_immune_player(max_reactions)
    if len(max_reactions) != 0:
        if there_is_no_equality:  # check if there is an equality
            if it_is_the_final:  # check if it's the last vote
                await close_final_vote(
                    max_reactions, reactions_list, cheaters_number, max_count
                )
            else:  # for other votes
                await close_normal(
                    max_reactions, reactions_list, cheaters_number, max_count, reactions
                )
        else:
            council_number = get_council_number()+1
            tied_players = [
                Player(letter=chr(EMOJIS_LIST.index(r) + 65)) for r in max_reactions
            ]
            if council_number != 1:  # if it's not the first vote
                await close_normal_equality(
                    reactions_list,
                    cheaters_number,
                    council_number,
                    it_is_the_final,
                    tied_players,
                )
            else:  # if it's the first vote
                await close_first_vote_equality(
                    reactions_list, cheaters_number, tied_players
                )
    else:
        await close_without_eliminated(
            max_reactions, reactions_list, cheaters_number, immune, reactions
        )
    if interaction:
        embed = discord.Embed(
            title=':robot: Le vote est clos :moyai:', color=COLOR_GREEN
        )
        await interaction.followup.send(embed=embed)
    logger.info('vote closing > OK')


async def eliminate(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: typing.Literal['After equality', 'Other reason'],
) -> None:
    logger.info(f'eliminate > start | member: {member} | reason: {reason}')
    eliminated = Player(id=member.id)
    players = Player(option='living')
    players_list = players.list
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    if reason == 'After equality':
        public_embed = discord.Embed(
            title='**{eliminated.nickname}**',
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
            value=f'Il reste {len(players_list)-1} aventuriers en jeu.',
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
        last_vote_log.update_eliminated(Player(id=member.id))
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
            value=f'Il reste {len(players_list)-1} aventuriers en jeu.',
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
            value=f"Il reste {len(Player(option='living').list)-1} aventuriers en jeu.",
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
