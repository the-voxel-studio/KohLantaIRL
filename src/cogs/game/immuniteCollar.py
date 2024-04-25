import discord
from discord import app_commands
from discord.ext import commands

from config.values import COLOR_GREEN
from utils.control import is_admin
from utils.game.immuniteCollar import (reset_immunite_collar,
                                       send_immunite_collar)
from utils.logging import get_logger

logger = get_logger(__name__)


class ImmuniteCollarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='send_immunite_collar', description="Envoi du collier d'immunité")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def send_immunite_collar(self, interaction: discord.Interaction):
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


async def setup(bot):
    await bot.add_cog(ImmuniteCollarCog(bot))
    logger.info('Loaded !')
