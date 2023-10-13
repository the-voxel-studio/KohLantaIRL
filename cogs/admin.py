import typing
from os import system

import discord
from discord import app_commands
from discord.ext import commands

from utils.logging import get_logger
from utils.log import send_log, send_logs_file

from config.values import CHANNEL_ID_BOT_LOGS, COLOR_GREEN, COLOR_ORANGE, COLOR_RED #OBLIGATOIRES (utilisation de la fonction eval)

logger = get_logger(__name__)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="send", description="Envoyer un message depuis Denis Brogniart"
    )
    async def send(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        content: str,
        color: typing.Literal["green", "orange", "red"],
    ):
        logger.info(
            f"Important message sending | Requested by {interaction.user} (id:{interaction.user.id}) | Channel id: {channel.id} | Color: {color} | Content: {content}"
        )
        self.embed = discord.Embed(
            title=f":robot: Information de {interaction.user.display_name} :moyai:",
            description=content,
            color=eval("COLOR_" + color.upper()),
        )
        await channel.send(embed=self.embed)
        await interaction.response.send_message(
            content=f"Message envoyé dans <#{channel.id}>"
        )

    @app_commands.command(
        name="reboot", description="Redémarre le serveur de Denis Brogniart"
    )
    async def reboot(self, interaction: discord.Interaction):
        logger.info(
            f"Preparing for manual reboot. | Requested by {interaction.user} (id:{interaction.user.id})"
        )
        await send_log(
            "Redémarrage manuel en cours",
            f"by **{interaction.user.display_name}**",
            color="orange",
        )
        logger.info("Ready to reboot.")
        system("sudo reboot")

    @app_commands.command(name = "logs", description = "To receive the bot.log file.")
    async def logs(self, interaction: discord.Interaction):
        logger.info(f"Send Logs File > start | requested by: {interaction.user} (id:{interaction.user.id})")
        await interaction.response.defer()
        await send_logs_file()
        self.embed=discord.Embed(title=f":robot: Logs disponible :moyai:", description=f":file_folder: Le fichier contenant mes logs est disponible dans ce channel: <#{CHANNEL_ID_BOT_LOGS}>.", color=COLOR_GREEN)
        self.embed.set_footer(text="Ce fichier est strictement confidentiel et son accès est réservé aux administrateurs du serveur.")
        await interaction.followup.send(embed=self.embed)
        logger.info(f"Send Logs File > OK | requested by: {interaction.user} (id:{interaction.user.id})")

    @app_commands.command(name = "clear", description = "Supprimer un certain nombre de messages")
    async def clear(self, interaction: discord.Interaction, amount: int):
        logger.info(f"Partial channel clearing | Requested by {interaction.user} (id:{interaction.user.id}) | Number: {amount} | Channel id: {interaction.channel.id}")
        await interaction.channel.purge(limit=amount)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
    logger.info(f"Loaded !")
