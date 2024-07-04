import random

import discord

from config.values import (CHANNEL_ID_GENERAL, CHANNEL_RULES, COLOR_GREEN,
                           EMOJI_ID_COLLIER, EMOJIS_LIST, GUILD_ID)
from database.game import Game
from database.player import Player
from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)


async def move_immunite_collar_down() -> None:
    """Move the immunite collar down in the general channel."""

    logger.info('fn > Move Immunite Collar Down > start')
    ic_msg_id = Game.immunite_collar_msg_id
    if ic_msg_id != 0:
        ic_msg = await bot.get_channel(CHANNEL_ID_GENERAL).fetch_message(ic_msg_id)
        await ic_msg.remove_reaction(f'<:collierimmunite:{EMOJI_ID_COLLIER}>', bot.user)
        await send_immunite_collar()
    logger.info('fn > Move Immunite Collar Down > ok')


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
        ic_msg = await bot.get_channel(CHANNEL_ID_GENERAL).fetch_message(ic_msg_id)
        await ic_msg.remove_reaction(f'<:collierimmunite:{EMOJI_ID_COLLIER}>', bot.user)
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


async def give_ephemeral_immunity(
    player: discord.Member
) -> None:
    """Give the ephemeral immunity to the player."""

    logger.info('fn > Give Ephemeral Immunity > start')
    Game.add_ephemerally_imunized_player_id(player.id)
    embed = discord.Embed(
        title="**On te l'a donné !**",
        description='De tous les aventuriers, tu es sans aucun doute le plus malin !',
        color=COLOR_GREEN,
    )
    embed.set_author(
        name='Immunité éphémère',
        icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
    )
    embed.set_thumbnail(
        url='https://static.wikia.nocookie.net/kohlanta/images/0/00/Totem_koh_lanta_2016.jpg/revision/latest?cb=20160915134322&path-prefix=fr'
    )
    embed.add_field(
        name='Tu es maintenant immunisé.',
        value=f"Si tu es choisi lors du prochain vote, ce bonus te protégera automatiquement.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    embed.set_image(
        url='https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif'
    )
    await player.send(embed=embed)
    logger.info('fn > Give Ephemeral Immunity > OK')


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


async def remove_ephemeral_immunity(
    player: discord.Member, admin: discord.Member
) -> None:
    """Remove the ephemeral immunity to the player."""

    logger.info('fn > Remove Ephemeral Immunity > start')
    if Game.remove_ephemerally_imunized_player_id(player.id):
        embed = discord.Embed(
            title="**On te l'a retiré !**",
            description='De tous les aventuriers, tu es sans aucun doute le plus triste !',
            color=COLOR_GREEN,
        )
        embed.set_author(
            name='Immunité éphémère',
            icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp',
        )
        embed.set_thumbnail(
            url='https://static.wikia.nocookie.net/kohlanta/images/0/00/Totem_koh_lanta_2016.jpg/revision/latest?cb=20160915134322&path-prefix=fr'
        )
        embed.add_field(
            name="Tu __n'__ es maintenant __plus__ immunisé.",
            value=f"Si tu es choisi lors du prochain vote, ce bonus ne te protégera plus.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
            inline=False,
        )
        embed.add_field(
            name="Ce bonus t'as été retiré par un administrateur.",
            value=f"N'hésite pas à contacter <@{admin.id}> pour plus d'informations.",
            inline=False,
        )
        embed.set_image(
            url='https://i.gifer.com/jQ.gif'
        )
        await player.send(embed=embed)
    logger.info('fn > Remove Ephemeral Immunity > OK')


async def remove_collar_immunized_loosers(max_reactions) -> list:
    """Remove the potential immune by collar player from the max reactions."""
    # [ ] optimize database requests for immunities removal

    logger.info('fn > Remove Potential Immune Player > start')

    immune_players__id = Game.collar_imunized_players_id
    eliminated = [r for r in max_reactions if Player(letter=chr(EMOJIS_LIST.index(r) + 65)).object._id in immune_players__id]
    immune = [r for r in max_reactions if r not in eliminated]

    if len(immune) > 0:
        await reset_immunite_collar()
        await send_immunite_collar_used(immune)
    else:
        immune = None

    logger.info('fn > Remove Potential Immune Player > ok')

    return eliminated, immune


async def remove_ephemerally_immunized_loosers(max_reactions) -> list:
    """Remove the potential ephemerally immunised player from the max reactions."""

    logger.info('fn > Remove Potential Ephemerally Imunised Player > start')

    immune_players__id = Game.ephemerally_imunized_players_id
    eliminated = [r for r in max_reactions if Player(letter=chr(EMOJIS_LIST.index(r) + 65)).object._id in immune_players__id]
    immune = [r for r in max_reactions if r not in eliminated]

    if len(immune) > 0:
        Game.ephemerally_imunized_players_id = []
        await send_ephemeral_immunity_used(immune)
    else:
        immune = None

    logger.info('fn > Remove Potential Ephemerally Imunised Player > ok')

    return eliminated, immune


async def send_immunite_collar_used(immune: list) -> None:
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

    for i in immune:
        i_p = Player(letter=chr(EMOJIS_LIST.index(i) + 65))
        member = guild.get_member(i_p.object.id)
        await member.send(embed=private_embed)

    logger.info('fn > Send Immunite Collar Used > ok')


async def send_ephemeral_immunity_used(immune: list) -> None:
    """Send the ephemeral immune used to the player."""

    logger.info('fn > Send Ephemeral Immune Used > start')
    private_embed = discord.Embed(
        title=':robot: **Tu as été sauvé !** :moyai:',
        description="Ton immunité éphémère t'a servi ce soir !",
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
        value=f"Si tu es choisi lors d'un prochain vote, ce bonus ne te protégera plus.\nPlus d'infos ici: <#{CHANNEL_RULES}>",
        inline=False,
    )
    private_embed.set_image(
        url='https://gifsec.com/wp-content/uploads/2022/09/congrats-gif-1.gif'
    )
    guild = bot.get_guild(GUILD_ID)

    for i in immune:
        i_p = Player(letter=chr(EMOJIS_LIST.index(i) + 65))
        member = guild.get_member(i_p.object.id)
        await member.send(embed=private_embed)

    logger.info('fn > Send Ephemeral Immune Used > ok')
