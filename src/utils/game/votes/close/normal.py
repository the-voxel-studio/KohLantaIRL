import datetime

import discord

from config.values import CHANNEL_ID_RESULTATS, EMOJIS_LIST, GUILD_ID
from database.game import Game
from database.player import Player
from database.votelog import VoteLog, get_council_number
from utils.bot import bot
from utils.log import get_logger
from utils.pdf import generate as pdfGenerate

logger = get_logger(__name__)


async def close_normal(
    max_reactions, reactions_list, cheaters_number, max_count, reactions
) -> None:
    """Close the normal vote."""

    logger.info('close_normal > start ')
    eliminated = Player(letter=chr(EMOJIS_LIST.index(max_reactions[0]) + 65))
    new_vote_log = VoteLog(data={
        'votes': reactions_list,
        'eliminated': [eliminated.object._id],
        'cheaters_number': cheaters_number
    })
    new_vote_log.save()
    nb_remaining_players = len(reactions) - 1
    embed = discord.Embed(
        title=f'**{eliminated.object.nickname}**',
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
    file_path = pdfGenerate(new_vote_log.object.number)
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
    logger.warning(f'eliminated: {eliminated.object.nickname} (id: {eliminated.object.id})')
    member = guild.get_member(eliminated.object.id)
    await member.send(embed=embed)
    role = discord.utils.get(guild.roles, name='Joueur')
    new_role = discord.utils.get(guild.roles, name='Eliminé')
    await member.remove_roles(role)
    await member.add_roles(new_role)
    eliminated.eliminate()
    if nb_remaining_players == 1:
        Game.wait_for_last_vote()
    logger.info('close_normal > OK ')
