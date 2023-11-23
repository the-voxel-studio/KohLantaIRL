import typing
from os import system, name as os_name

import discord
from discord import app_commands
from discord.ext import commands

from config.values import (  # OBLIGATOIRES (utilisation de la fonction eval)
    CHANNEL_ID_BOT_LOGS, COLOR_GREEN, COLOR_ORANGE, COLOR_RED)
from utils.log import send_log, send_logs_file
from utils.logging import get_logger
from utils.control import is_admin, is_in_guild

logger = get_logger(__name__)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="send", description="Envoyer un message depuis Denis Brogniart"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def send(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        content: str,
        color: typing.Literal["green", "orange", "red"],
    ):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
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
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def reboot(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        if os_name == "posix":
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
        else:
            logger.error(f"Manual reboot is only possible on posix server | Requested by {interaction.user} (id:{interaction.user.id})")

    @app_commands.command(
        name="shutdown", description="Eteind le serveur de Denis Brogniart"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def shutdown(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        if os_name == "posix":
            logger.info(
                f"Preparing for shutdown. | Requested by {interaction.user} (id:{interaction.user.id})"
            )
            await send_log(
                "Extinction manuelle en cours",
                f"by **{interaction.user.display_name}**",
                color="orange",
            )
            logger.info("Ready to shutdown.")
            system("sudo halt")
        else:
            logger.error(f"Manual shutdown is only possible on posix server | Requested by {interaction.user} (id:{interaction.user.id})")

    @app_commands.command(name = "logs", description = "To receive the bot.log file.")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def logs(self, interaction: discord.Interaction):
        logger.info(f"Send Logs File > start | requested by: {interaction.user} (id:{interaction.user.id})")
        await interaction.response.defer()
        await send_logs_file()
        self.embed=discord.Embed(title=f":robot: Logs disponible :moyai:", description=f":file_folder: Le fichier contenant mes logs est disponible dans ce channel: <#{CHANNEL_ID_BOT_LOGS}>.", color=COLOR_GREEN)
        self.embed.set_footer(text="Ce fichier est strictement confidentiel et son accès est réservé aux administrateurs du serveur.")
        await interaction.followup.send(embed=self.embed)
        logger.info(f"Send Logs File > OK | requested by: {interaction.user} (id:{interaction.user.id})")

    @app_commands.command(name = "clear", description = "Supprimer un certain nombre de messages")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        logger.info(f"Partial channel clearing | Requested by {interaction.user} (id:{interaction.user.id}) | Number: {amount} | Channel id: {interaction.channel.id}")
        await interaction.channel.purge(limit=amount)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
    logger.info(f"Loaded !")
