import discord

from config.values import CHANNEL_ID_VOTE, COLOR_GREEN, EMOJIS_LIST
from database.game import Game
from database.player import Player
from database.votelog import get_council_number
from utils.bot import bot
from utils.game.immunity.collar import remove_collar_immunized_loosers
from utils.game.immunity.ephemeral import remove_ephemerally_immunized_loosers
from utils.log import get_logger

from .. import arrange_votes, count_votes, deal_with_cheaters
from . import (close_final_vote, close_first_vote_equality, close_normal,
               close_normal_equality, close_without_eliminated)

logger = get_logger(__name__)


async def close(interaction: discord.Interaction = None) -> None:
    """Close the vote."""

    # [ ] ? save immune persons in VoteLog
    # [ ] admin aprobation before announce ?
    logger.info('vote closing > start')
    channel = bot.get_channel(CHANNEL_ID_VOTE)
    msg = await channel.fetch_message(Game.vote_msg_id)
    reactions = msg.reactions
    reactions_list = await arrange_votes(reactions)
    await msg.delete()
    Game.vote_msg_id = 0
    cheaters_number = await deal_with_cheaters(reactions_list, reactions)
    max_reactions, max_count, it_is_the_final, there_is_no_equality = await count_votes(
        reactions
    )
    if not it_is_the_final:
        max_reactions, immune1 = await remove_collar_immunized_loosers(max_reactions)
        max_reactions, immune2 = await remove_ephemerally_immunized_loosers(max_reactions)
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
            council_number = get_council_number() + 1
            tied_players = [
                Player(letter=chr(EMOJIS_LIST.index(r) + 65)).object for r in max_reactions
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
            max_reactions, reactions_list, cheaters_number, immune1 + immune2, reactions
        )
    if interaction:
        embed = discord.Embed(
            title=':robot: Le vote est clos :moyai:', color=COLOR_GREEN
        )
        await interaction.followup.send(embed=embed)
    logger.info('vote closing > OK')
