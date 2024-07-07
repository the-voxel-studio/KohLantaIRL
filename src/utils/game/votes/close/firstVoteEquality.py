import datetime

import discord

from config.values import CHANNEL_ID_RESULTATS, GUILD_ID
from database.votelog import VoteLog
from utils.bot import bot
from utils.log import get_logger
from utils.pdf import generate as pdfGenerate

logger = get_logger(__name__)


async def close_first_vote_equality(
    reactions_list, cheaters_number, tied_players
) -> None:
    """Close the first vote after an equality."""
    # CHECK eliminated players data type

    logger.info('close_first_vote_equality > start ')
    new_vote_log = VoteLog(data={
        'votes': reactions_list,
        'eliminated': tied_players,
        'cheaters_number': cheaters_number,
        'tied_players': tied_players,
        'hidden': False
    })
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
    file_path = pdfGenerate(new_vote_log.object.number)
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
