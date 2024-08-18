import random

import discord

from config.values import (CHANNEL_ID_GENERAL, CHANNEL_RULES, COLOR_GREEN,
                           EMOJI_ID_COLLIER, EMOJIS_LIST, GUILD_ID)
from database.game import Game
from database.player import Player, PlayerList
from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)


async def move_immunite_collar_down() -> None:
    """Move the immunite collar down in the general channel."""

    logger.info('fn > Move Immunite Collar Down > start')
    ic_msg_id = Game.immunite_collar_msg_id
    if ic_msg_id != 0:
        try:
            ic_msg = await bot.get_channel(CHANNEL_ID_GENERAL).fetch_message(ic_msg_id)
            await ic_msg.remove_reaction(f'<:collierimmunite:{EMOJI_ID_COLLIER}>', bot.user)
            await send_immunite_collar()
            logger.info('fn > Move Immunite Collar Down > ok')
        except discord.errors.NotFound:
            logger.warning('fn > Move Immunite Collar Down > Immunite Collar Message Not found')


async def send_immunite_collar() -> None:
    """Send the immunite collar in the general channel."""

    # CHECK automatic sending
    logger.info('fn > Send Immunite Collar > start')
    channel = bot.get_channel(CHANNEL_ID_GENERAL)
    msgs = [msg async for msg in channel.history(limit=20)][5:]
    msg = random.choice(msgs)
    await msg.add_reaction(f'<:collierimmunite:{EMOJI_ID_COLLIER}>')
    Game.immunite_collar_msg_id = msg.id
    logger.info('fn > Send Immunite Collar > OK')


async def reset_immunite_collar() -> None:
    """Reset the immunite collar."""

    logger.info('fn > Reset Immunite Collar > start')
    ic_msg_id = Game.immunite_collar_msg_id
    if ic_msg_id != 0:
        try:
            ic_msg = await bot.get_channel(CHANNEL_ID_GENERAL).fetch_message(ic_msg_id)
            await ic_msg.remove_reaction(f'<:collierimmunite:{EMOJI_ID_COLLIER}>', bot.user)
        except discord.errors.NotFound:
            logger.warning('fn > Reset Immunite Collar > Immunite Collar Message Not found')
    Game.immunite_collar_msg_id = 0
    Game.collar_imunized_players_id = []
    logger.info('fn > Reset Immunite Collar > OK')


async def give_immunite_collar(
    payload: discord.RawReactionActionEvent, player: Player
) -> None:
    """Give the immunite collar to the player. (if the player is the one who found it)"""

    logger.info('fn > Give Immunite Collar > start')
    Game.add_collar_imunized_player_id(player.object.id)
    Game.immunite_collar_msg_id = 0
    embed = discord.Embed(
        title="**Tu l'as trouvé !**",
        description='De tous les aventuriers, tu es sans aucun doute le plus malin !',
        color=COLOR_GREEN,
    )
    embed.set_author(
        name="Collier d'immunité",
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/emojis/1145354940705943652.webp?size=100&quality=high'
    )
    embed.add_field(
        name='Tu es maintenant immunisé.',
        value=f"Si tu es choisi lors d'un prochain vote, ce collier te protégera automatiquement.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    embed.set_image(
        url='https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif'
    )
    await payload.member.send(embed=embed)
    logger.info('fn > Give Immunite Collar > OK')


async def give_immunite_collar_by_command(
    player: discord.Member
) -> None:
    """Give the immunite collar to the player. (if it is giving by an admin)"""
    # CHECK voir comment faire si deux immunisés

    logger.info('fn > Give Immunite Collar By Command > start')
    Game.add_collar_imunized_player_id(player.id)
    embed = discord.Embed(
        title="**On te l'a donné !**",
        description='De tous les aventuriers, tu es sans aucun doute le plus malin !',
        color=COLOR_GREEN,
    )
    embed.set_author(
        name="Collier d'immunité",
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/emojis/1145354940705943652.webp?size=100&quality=high'
    )
    embed.add_field(
        name='Tu es maintenant immunisé.',
        value=f"Si tu es choisi lors d'un prochain vote, ce collier te protégera automatiquement.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    embed.set_image(
        url='https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif'
    )
    await player.send(embed=embed)
    logger.info('fn > Give Immunite Collar By Command > OK')


async def remove_immunite_collar(
    player: discord.Member, admin: discord.Member
) -> None:
    """Remove the immunite collar to the player."""

    logger.info('fn > Remove Immunite Collar > start')
    if Game.remove_collar_imunized_player_id(player.id):
        embed = discord.Embed(
            title="**On te l'a retiré !**",
            description='De tous les aventuriers, tu es sans aucun doute le plus triste !',
            color=COLOR_GREEN,
        )
        embed.set_author(
            name="Collier d'immunité",
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/emojis/1145354940705943652.webp?size=100&quality=high'
        )
        embed.add_field(
            name="Tu __n'__ es maintenant __plus__ immunisé.",
            value=f"Si tu es choisi lors d'un prochain vote, le collier ne te protégera plus.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
            inline=False,
        )
        embed.add_field(
            name="Le collier t'as été retiré par un administrateur.",
            value=f"N'hésite pas à contacter <@{admin.id}> pour plus d'informations.",
            inline=False,
        )
        embed.set_image(
            url='https://i.gifer.com/jQ.gif'
        )
        await player.send(embed=embed)
    logger.info('fn > Remove Immunite Collar > OK')


async def remove_collar_immunized_loosers(max_reactions) -> tuple[list, PlayerList]:
    """Remove the potential immune by collar player from the max reactions."""
    # [ ] optimize database requests for immunities removal

    logger.info('fn > Remove Potential Immune Player > start')

    immune_players_id = Game.collar_imunized_players_id
    eliminated = [
        r
        for r in max_reactions
        if Player(letter=chr(EMOJIS_LIST.index(r) + 65)).object.id not in immune_players_id
    ]
    immune = PlayerList([
        {'letter': chr(EMOJIS_LIST.index(r) + 65)}
        for r in max_reactions
        if r not in eliminated
    ])

    if len(immune) > 0:
        await reset_immunite_collar()
        await send_immunite_collar_used(immune)

    logger.info('fn > Remove Potential Immune Player > ok')

    return eliminated, immune


async def send_immunite_collar_used(immune: PlayerList) -> None:
    """Send the immunite collar used to the player."""

    logger.info('fn > Send Immunite Collar Used > start')
    private_embed = discord.Embed(
        title=':robot: **Tu as été sauvé !** :moyai:',
        description="Ton collier t'a servi ce soir !",
        color=COLOR_GREEN,
    )
    private_embed.set_author(
        name='Résultat du conseil',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    private_embed.set_thumbnail(
        url='https://cdn.discordapp.com/emojis/1145354940705943652.webp?size=100&quality=high'
    )
    private_embed.add_field(
        name="Tu n'es maintenant plus immunisé.",
        value=f"Si tu es choisi lors d'un prochain vote, ce collier ne te protégera plus.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    private_embed.set_image(
        url='https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif'
    )
    guild = bot.get_guild(GUILD_ID)

    for p in immune.objects:
        member = guild.get_member(p.object.id)
        await member.send(embed=private_embed)

    logger.info('fn > Send Immunite Collar Used > ok')
