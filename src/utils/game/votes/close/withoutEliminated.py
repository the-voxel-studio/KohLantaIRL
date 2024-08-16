import discord

from config.values import CHANNEL_ID_RESULTATS
from database.votelog import VoteLog, get_council_number
from utils.bot import bot
from utils.log import get_logger
from utils.pdf import generate as pdfGenerate

logger = get_logger(__name__)


async def close_without_eliminated(
    max_reactions, reactions_list, cheaters_number, immune, reactions
) -> None:
    """Close the vote without eliminated players."""

    logger.info('close_without_eliminated > start ')
    new_vote_log = VoteLog(data={
        'votes': reactions_list,
        'eliminated': [],
        'cheaters_number': cheaters_number,
    })
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
    file_path = pdfGenerate(new_vote_log.object.number)
    file = discord.File(file_path)
    channel = bot.get_channel(CHANNEL_ID_RESULTATS)
    await channel.send(embed=embed, file=file)
    logger.info('close_without_eliminated > OK ')
