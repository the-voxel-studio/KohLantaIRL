from discord.ext import commands
from discord import app_commands
import discord
from utils.logging import get_logger
from config.values import COLOR_GREEN
from utils.models import Variables

logger = get_logger(__name__)

class StepsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "start-game", description = "Démarre la partie de KohLanta (fermeture des inscriptions)")
    async def start(self, interaction: discord.Interaction):
        logger.info(f"Game start | Requested by {interaction.user} (id:{interaction.user.id}).")
        Variables.start_game()
        self.embed=discord.Embed(title=f":robot: Partie démarrée :moyai:", color=COLOR_GREEN)
        await interaction.response.send_message(embed=self.embed)

async def setup(bot):
    await bot.add_cog(StepsCog(bot))
    logger.info(f"Loaded !")