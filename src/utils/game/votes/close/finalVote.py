import discord

from config.values import (CHANNEL_ID_ANNONCES, COLOR_GREEN, EMOJIS_LIST,
                           GUILD_ID)
from database.player import Player
from database.votelog import VoteLog
from utils.bot import bot
from utils.game.alliances import purge_alliances
from utils.game.players import reset_roles
from utils.log import get_logger
from utils.pdf import generate as pdfGenerate

logger = get_logger(__name__)


async def close_final_vote(
    max_reactions, reactions_list, cheaters_number, max_count
) -> None:
    """Close the final vote."""

    logger.info('close_final_vote > start ')
    logger.info('EqualityView select_callback > start | max_rea')
    winner = Player(letter=chr(EMOJIS_LIST.index(max_reactions[0]) + 65))
    data = {
        'votes': reactions_list,
        'eliminated': [winner.object._id],
        'cheaters_number': cheaters_number,
        'hidden': False,
    }
    new_vote_log = VoteLog(data=data)
    new_vote_log.save()
    embed = discord.Embed(
        title=f'**{winner.object.nickname}** remporte la partie !',
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
    file_path = pdfGenerate(new_vote_log.object.number, final=True)
    file = discord.File(file_path)
    channel = bot.get_channel(CHANNEL_ID_ANNONCES)
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
        value=f"Plus d'infos ici: <#{CHANNEL_ID_ANNONCES}>.",
        inline=False,
    )
    embed.set_image(url='https://media.tenor.com/b4GVF1aUlgIAAAAC/chirac-victoire.gif')
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(winner.object.id)
    await member.send(embed=embed)
    await reset_roles('Joueur', 'Eliminé', 'Finaliste', 'Votant Final')
    await purge_alliances()
    logger.info('close_final_vote > OK ')
