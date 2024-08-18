import discord

from config.values import CHANNEL_RULES, COLOR_GREEN, EMOJIS_LIST, GUILD_ID
from database.game import Game
from database.player import Player, PlayerList
from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)


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


async def remove_ephemerally_immunized_loosers(max_reactions) -> tuple[list, PlayerList]:
    """Remove the potential ephemerally immunised player from the max reactions."""

    logger.info('fn > Remove Potential Ephemerally Imunised Player > start')

    immune_players_id = Game.ephemerally_imunized_players_id
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
        Game.ephemerally_imunized_players_id = []
        await send_ephemeral_immunity_used(immune)

    logger.info('fn > Remove Potential Ephemerally Imunised Player > ok')

    return eliminated, immune


async def send_ephemeral_immunity_used(immune: PlayerList) -> None:
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

    for p in immune.objects:
        member = guild.get_member(p.object.id)
        await member.send(embed=private_embed)

    logger.info('fn > Send Ephemeral Immune Used > ok')
