import discord
import discord.ext.commands

from config.values import (CHANNEL_ID_VOTE, COLOR_RED, EMOJI_ID_COLLIER, EMOJIS_LIST)
from database.game import Game
from database.player import Player
import discord.ext

from utils.bot import bot
from utils.game.immunity.collar import give_immunite_collar
from utils.logging import get_logger
from utils.punishments import timeout

logger = get_logger(__name__)


async def on_raw_reaction_add_event(payload) -> None:
    """Gestion des réactions ajoutées aux messages"""

    if payload.emoji.name in EMOJIS_LIST:
        emoji = chr(EMOJIS_LIST.index(payload.emoji.name) + 65)
    else:
        emoji = 'not an alphabet emoji'
    logger.info(
        f'New raw reaction | user: {payload.member} (id: {payload.member.id}) | msg id: {payload.message_id} | emoji: {emoji}'
    )
    user = payload.member
    if user.id != bot.user.id:
        player = Player(id=payload.user_id)
        channel = bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if isinstance(payload.emoji, discord.partial_emoji.PartialEmoji) and payload.emoji.id == EMOJI_ID_COLLIER:
            await msg.remove_reaction(payload.emoji, user)
            if msg.id == Game.immunite_collar_msg_id and Player(id=user.id).object.alive:
                await msg.clear_reaction(
                    f'<:collierimmunite:{EMOJI_ID_COLLIER}>'
                )
                await give_immunite_collar(payload, player)
            else:
                logger.warning(
                    f'Use of immunity collar in reaction by : {user} (id:{user.id}).'
                )
                logger.info(
                    'Sending a message reminding of the rules relating to the immunity collar.'
                )
                embed = discord.Embed(
                    title=':robot: RAPPEL AUX JOUEURS :moyai:',
                    description=f":no_entry: L'usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}> est interdit sur le serveur afin de ne pas embrouiller les joueurs à la recherche du collier d'immunité.",
                    color=COLOR_RED,
                )
                await channel.send(embed=embed, delete_after=20)
                await timeout(
                    user,
                    reason=f"Usage de l'emoji <:collierimmunite:{EMOJI_ID_COLLIER}>",
                )
        elif channel.id == CHANNEL_ID_VOTE and (
            not player.object._id or not player.object.alive
        ):
            if 'Votant Final' not in [r.name for r in user.roles]:
                await msg.remove_reaction(payload.emoji, user)
                logger.warning(
                    f'Vote received from an eliminated player. Sent by : {user} (id:{user.id}).'
                )
                embed = discord.Embed(
                    title=':robot: Action interdite :moyai:',
                    description=':no_entry: Les aventuriers éliminés ne peuvent pas participer au vote.',
                    color=COLOR_RED,
                )
                await user.send(embed=embed)
        elif channel.id == CHANNEL_ID_VOTE:
            users = []
            for react in msg.reactions:
                users += [user async for user in react.users()]
            if users.count(user) > 1:
                await msg.remove_reaction(payload.emoji, user)
