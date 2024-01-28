import random

import discord

from config.values import (
    CHANNEL_ID_GENERAL,
    CHANNEL_RULES,
    COLOR_GREEN,
    EMOJI_ID_COLLIER,
    EMOJIS_LIST,
    GUILD_ID
)
from utils.bot import bot
from utils.logging import get_logger
from utils.models import Player, Variables

logger = get_logger(__name__)

async def move_immunite_collar_down() -> None:
    logger.info("fn > Move Immunite Collar Down > start")
    ic_msg_id = Variables.get_immunite_collar_msg_id()
    if ic_msg_id != 0:
        ic_msg = await bot.get_channel(CHANNEL_ID_GENERAL).fetch_message(ic_msg_id)
        await ic_msg.remove_reaction(f"<:collierimmunite:{EMOJI_ID_COLLIER}>", bot.user)
        await send_immunite_collar()
    logger.info("fn > Move Immunite Collar Down > ok")

async def send_immunite_collar() -> None:
    # TODO automatic sending
    logger.info("fn > Send Immunite Collar > start")
    channel = bot.get_channel(CHANNEL_ID_GENERAL)
    msgs = [msg async for msg in channel.history(limit=20)][5:]
    msg = random.choice(msgs)
    await msg.add_reaction(f"<:collierimmunite:{EMOJI_ID_COLLIER}>")
    Variables.set_immunite_collar_msg_id(msg.id)
    logger.info("fn > Send Immunite Collar > OK")

async def reset_immunite_collar() -> None:
    logger.info("fn > Reset Immunite Collar > start")
    ic_msg_id = Variables.get_immunite_collar_msg_id()
    if ic_msg_id != 0:
        ic_msg = await bot.get_channel(CHANNEL_ID_GENERAL).fetch_message(ic_msg_id)
        await ic_msg.remove_reaction(f"<:collierimmunite:{EMOJI_ID_COLLIER}>", bot.user)
    Variables.set_immunite_collar_msg_id(0)
    Variables.set_immunite_collar_player_id(0)
    logger.info("fn > Reset Immunite Collar > OK")

async def give_immunite_collar(
    payload: discord.RawReactionActionEvent, player: Player
) -> None:
    logger.info("fn > Give Immunite Collar > start")
    Variables.set_immunite_collar_player_id(player._id)
    Variables.set_immunite_collar_msg_id(0)
    embed = discord.Embed(
        title=f"**Tu l'as trouvé !**",
        description=f"De tous les aventuriers, tu es sans aucun doute le plus malin !",
        color=COLOR_GREEN,
    )
    embed.set_author(
        name="Collier d'immunité",
        icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp",
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/1145354940705943652.webp?size=100&quality=high"
    )
    embed.add_field(
        name=f"Tu es maintenant immunisé.",
        value=f"Si tu es choisi lors d'un prochain vote, ce collier te protégera automatiquement.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    embed.set_image(
        url="https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif"
    )
    await payload.member.send(embed=embed)
    logger.info("fn > Give Immunite Collar > OK")

async def remove_potential_immune_player(max_reactions) -> list:
    # CHECK remove immunite
    logger.info("fn > Remove Potential Immune Player > start")
    immune_player__id = Variables.get_immunite_collar_player_id()
    eliminated = [r for r in max_reactions if Player(letter=chr(EMOJIS_LIST.index(r) + 65))._id != immune_player__id]
    immune = [r for r in max_reactions if r not in eliminated]
    if len(immune) > 0: 
        immune = immune[0]
        await reset_immunite_collar()
        await send_immunite_collar_used(immune)
    else: immune = None
    logger.info("fn > Remove Potential Immune Player > ok")
    return eliminated, immune

async def send_immunite_collar_used(immune) -> None:
    logger.info("fn > Send Immunite Collar Used > start")
    immune = Player(letter=chr(EMOJIS_LIST.index(immune) + 65))
    private_embed = discord.Embed(
        title=f":robot: **Tu as été sauvé !** :moyai:",
        description=f"Ton collier t'a servi ce soir !",
        color=COLOR_GREEN,
    )
    private_embed.set_author(
        name="Résultat du conseil",
        icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp",
    )
    private_embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/1145354940705943652.webp?size=100&quality=high"
    )
    private_embed.add_field(
        name=f"Tu n'es maintenant plus immunisé.",
        value=f"Si tu es choisi lors d'un prochain vote, ce collier ne te protégera plus.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    private_embed.set_image(
        url="https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif"
    )
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(immune.id)
    await member.send(embed=private_embed)
    logger.info("fn > Send Immunite Collar Used > ok")