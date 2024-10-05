import discord
from discord import app_commands
from discord.ext import commands

from config.values import COLOR_GREEN
from utils.control import is_admin
from utils.game.immunity.collar import give_immunite_collar_by_command
from utils.game.immunity.collar import \
    remove_immunite_collar as remove_immunite_collar_util
from utils.game.immunity.collar import (reset_immunite_collar,
                                        send_immunite_collar)
from utils.game.immunity.ephemeral import \
    give_ephemeral_immunity as give_ephemeral_immunity_util
from utils.game.immunity.ephemeral import \
    remove_ephemeral_immunity as remove_ephemeral_immunity_util
from utils.logging import get_logger

logger = get_logger(__name__)


class ImmuniteCollarCog(commands.Cog):
    """Immunite Collar commands cog."""

    def __init__(self, bot):
        """Init the cog."""

        self.bot = bot

    @app_commands.command(name='send_immunite_collar', description="Envoi du collier d'immunité")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def send_immunite_collar(self, interaction: discord.Interaction):
        """Send the immunite collar to a player."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        await interaction.response.defer()
        logger.info(
            f'Immunite Collar Sended | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await send_immunite_collar()
        self.embed = discord.Embed(
            title=":robot: Collier d'immunité envoyé :moyai:", color=COLOR_GREEN
        )
        await interaction.followup.send(embed=self.embed)

    @app_commands.command(name='reset_immunite_collar', description="Réinitialisation du collier d'immunité")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def reset_immunite_collar(self, interaction: discord.Interaction):
        """Reset the immunite collar."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        await interaction.response.defer()
        logger.info(
            f'Immunite Collar Reset | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await reset_immunite_collar()
        self.embed = discord.Embed(
            title=":robot: Collier d'immunité réinitialisé :moyai:", color=COLOR_GREEN
        )
        await interaction.followup.send(embed=self.embed)

    @app_commands.command(name='give_immunite_collar', description="Donner le collier d'immunité")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    @app_commands.describe(player="Joueur à qui donner le collier d'immunité")
    async def give_immunite_collar(self, interaction: discord.Interaction, player: discord.Member):
        """Give the immunite collar to a player."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        await interaction.response.defer()
        logger.info(
            f'Immunite Collar Given | To {player} (id:{player.id}) | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await give_immunite_collar_by_command(player)
        self.embed = discord.Embed(
            title=":robot: Collier d'immunité donné :moyai:", color=COLOR_GREEN
        )
        self.embed.add_field(
            name='Joueur concerné',
            value=f':bust_in_silhouette: : <@{player.id}>'
        )
        await interaction.followup.send(embed=self.embed)

    @app_commands.command(name='give_ephemeral_immunity', description='Donner une immunité éphémère')
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    @app_commands.describe(player="Joueur à qui donner l'immunité'")
    async def give_ephemeral_immunity(self, interaction: discord.Interaction, player: discord.Member):
        """Give the ephemeral immunity to a player."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        await interaction.response.defer()
        logger.info(
            f'Ephemeral Immunity Given | To {player} (id:{player.id}) | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await give_ephemeral_immunity_util(player)
        self.embed = discord.Embed(
            title=':robot: Immmunité Ephémère donnée :moyai:', color=COLOR_GREEN
        )
        self.embed.add_field(
            name='Joueur concerné',
            value=f':bust_in_silhouette: : <@{player.id}>'
        )
        await interaction.followup.send(embed=self.embed)

    @app_commands.command(name='remove_immunite_collar', description="Retirer un collier d'immunité")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    @app_commands.describe(player="Joueur à qui retirer l'immunité'")
    async def remove_immunite_collar(self, interaction: discord.Interaction, player: discord.Member):
        """Remove the immunite collar to a player."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        await interaction.response.defer()
        logger.info(
            f'Immunite Collar Removed | To {player} (id:{player.id}) | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await remove_immunite_collar_util(player, interaction.user)
        self.embed = discord.Embed(
            title=":robot: Collier d'immunitée retiré :moyai:", color=COLOR_GREEN
        )
        self.embed.add_field(
            name='Joueur concerné:',
            value=f':bust_in_silhouette: : <@{player.id}>'
        )
        await interaction.followup.send(embed=self.embed)

    @app_commands.command(name='remove_ephemeral_immunity', description='Retirer une immunité éphémère')
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    @app_commands.describe(player="Joueur à qui retirer l'immunité'")
    async def remove_ephemeral_immunity(self, interaction: discord.Interaction, player: discord.Member):
        """Remove the ephemeral immunity to a player."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        await interaction.response.defer()
        logger.info(
            f'Ephemeral Immunity Removed | To {player} (id:{player.id}) | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await remove_ephemeral_immunity_util(player, interaction.user)
        self.embed = discord.Embed(
            title=':robot: Immmunité Ephémère retirée :moyai:', color=COLOR_GREEN
        )
        self.embed.add_field(
            name='Joueur concerné:',
            value=f':bust_in_silhouette: : <@{player.id}>'
        )
        await interaction.followup.send(embed=self.embed)


async def setup(bot):
    """Setup the cog."""

    await bot.add_cog(ImmuniteCollarCog(bot))
    logger.debug('Loaded !')
