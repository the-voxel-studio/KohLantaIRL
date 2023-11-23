import discord
from discord import app_commands
from discord.ext import commands

from config.values import COLOR_GREEN
from utils.logging import get_logger
from utils.models import Variables
from utils.control import is_admin

logger = get_logger(__name__)

class StepsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "open_joining", description = "Ouverture des inscriptions")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def open_joining(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Joining opening | Requested by {interaction.user} (id:{interaction.user.id}).")
        Variables.open_joining()
        self.embed=discord.Embed(title=f":robot: Inscriptions ouvertes :moyai:", color=COLOR_GREEN)
        await interaction.response.send_message(embed=self.embed)

    @app_commands.command(name = "start_game", description = "Démarre la partie de KohLanta (fermeture des inscriptions)")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def start(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Game start | Requested by {interaction.user} (id:{interaction.user.id}).")
        Variables.start_game()
        self.embed=discord.Embed(title=f":robot: Partie démarrée :moyai:", color=COLOR_GREEN)
        await interaction.response.send_message(embed=self.embed)

async def setup(bot):
    await bot.add_cog(StepsCog(bot))
    logger.info(f"Loaded !")