from utils.models import Player, NewAlliance, Alliance
from utils.logging import get_logger
from utils.bot import bot

from config.values import GUILD_ID, CATEGORIE_ID_ALLIANCES, COLOR_GREEN, COLOR_ORANGE

import discord

logger = get_logger(__name__)


async def new_alliance(interaction: discord.Interaction):
    player = Player(id=interaction.user.id)
    channel_name = 'new_channel_' + '_'.join(interaction.user.nick.lower().split(' '))
    same_named_alliance_by_channels = discord.utils.get(
        interaction.guild.channels, name=channel_name
    )
    if not player.alive:
        logger.warning(
            f'EliminatedPlayer | Sent by {interaction.user} (id:{interaction.user.id}) | Attempted to use the command: /alliance'
        )
        embed = discord.Embed(
            title=':robot: Action impossible :moyai:',
            description=":warning: Impossible d'effectuer l'action demandée : les joueurs éliminés ne peuvent pas créer d'alliance.",
            color=COLOR_ORANGE,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    elif same_named_alliance_by_channels:
        logger.warning(
            f'AlreadyHaveNewAlliance | Sent by {interaction.user} (id:{interaction.user.id}) | Attempted to use the command: /alliance'
        )
        embed = discord.Embed(
            title=':robot: Action impossible :moyai:',
            description=f":warning: Impossible d'effectuer l'action demandée : vous disposez déjà d'une alliance neuve, non renommée et sans membre (excepté vous). Rendez-vous ici <#{same_named_alliance_by_channels.id}> pour la renommer !",
            color=COLOR_ORANGE,
        )
        embed.set_footer(
            text="Pas d'inquiétude, seul toi peut voir ce message. Aucun autre joueur, pas même les administrateurs, voient que tu as tenté de créer une alliance."
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        logger.info(
            f'New alliance creation started | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        same_named_alliance_by_db = Alliance(name=channel_name)
        if same_named_alliance_by_db.exists:
            same_named_alliance_by_db.delete(interaction.user)
        general_guild = bot.get_guild(GUILD_ID)
        guild = discord.utils.get(general_guild.categories, id=CATEGORIE_ID_ALLIANCES)
        overwrites = {
            general_guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
        }
        new_text_channel = await guild.create_text_channel(
            channel_name, overwrites=overwrites
        )
        new_voice_channel = await guild.create_voice_channel(
            channel_name, overwrites=overwrites
        )
        new_alliance = NewAlliance()
        new_alliance.text_id = new_text_channel.id
        new_alliance.voice_id = new_voice_channel.id
        new_alliance.name = channel_name
        new_alliance.creator = player._id
        new_alliance.save()
        embed = discord.Embed(
            title=':robot: ✏️ Renomme ton alliance dès maintenant ! :moyai:',
            description="Tu dois d'abord renommer ton alliance afin de pouvoir ajouter des membres.",
        )
        embed.add_field(
            name="/nom 'nouveau-nom-de-l-alliance'",
            value="L'expression 'nouveau-nom-de-l-alliance' est à remplacer par le nouveau nom que vous souhaitez définir.",
        )
        await new_text_channel.send(embed=embed)
        embed = discord.Embed(
            title=':robot: Nouvelle alliance :moyai:',
            description=":white_check_mark: L'alliance {channel_name} a bien été créée : rendez-vous ici <#{new_text_channel.id}> pour la renommer !",
            color=COLOR_GREEN,
        )
        embed.set_footer(
            text="Pas d'inquiétude, seul toi peut voir ce message. Aucun autre joueur, pas même les administrateurs, voient que tu as créé une alliance."
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(
            f'New Alliance created | Requested by {interaction.user} (id:{interaction.user.id}) | Alliance text channel id: {new_text_channel.id}'
        )


async def close_alliance(
    txt_channel_id: discord.TextChannel.id, user: discord.User = None
):
    logger.info(
        f'fn > Alliance Close > start | Requested by {user} (id:{user.id}) | Alliance text channel id: {txt_channel_id}'
    )
    alliance = Alliance(text_id=txt_channel_id)
    text_channel = bot.get_channel(alliance.text_id)
    voice_channel = bot.get_channel(alliance.voice_id)
    await text_channel.delete()
    await voice_channel.delete()
    alliance.close(user)
    logger.info(
        f'fn > Alliance Close > OK | Requested by {user} (id:{user.id}) | Alliance text channel id: {txt_channel_id} | Alliance voice channel id: {alliance.voice_id}'
    )


async def purge_empty_alliances():
    logger.info('fn > Empty Alliances Purge > start')
    Alliance().purge_empty_alliances()
    logger.info('fn > Empty Alliances Purge > OK')


async def purge_alliances(interaction: discord.Interaction = None):
    logger.info('fn > Alliances Purge > start')
    category = bot.get_channel(CATEGORIE_ID_ALLIANCES)
    for channel in category.channels:
        logger.info(f'fn > Alliances Purge > delete {channel.name} alliance')
        await channel.delete()
    embed = discord.Embed(
        title=':robot: Suppression des alliances :moyai:',
        description='Toutes les alliances ont été supprimées.',
        color=COLOR_GREEN,
    )
    if interaction:
        await interaction.followup.send(embed=embed)
    logger.info('fn > Alliances Purge > OK')
