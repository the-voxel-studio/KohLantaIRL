import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.bot import bot
from utils.logging import get_logger

logger = get_logger(__name__)


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Commands infos")
    @app_commands.guild_only()
    async def help(self, interaction: discord.Interaction, command: str = None):
        if command is not None:
            for c in bot.tree.get_commands():
                if c.name == command:
                    command = c
                    break
                else:
                    continue
            try:
                txt = command.description
                embed = discord.Embed(title=command.name, description=txt)
                await interaction.response.send_message(embed=embed)
            except AttributeError:  # command not found
                e = discord.Embed(
                    title="Error:",
                    description=f"Command {command} not found",
                    color=0xFF0000,
                )
                await interaction.response.send_message(embed=e)
            return
        command_dict = {}
        available_commands = ""
        for command in bot.tree.get_commands():
            module = ".".join(command.module.split(".")[1:])
            if command_dict.get(module):
                command_dict[module].append(f"{command.name} : {command.description}")
            else:
                command_dict[module] = [f"{command.name} : {command.description}"]
        for cog in command_dict:
            commands = command_dict.get(cog)
            available_commands += "### " + (cog) + " :\n"
            for c in commands:
                available_commands += "- " + c + "\n"
        embed = discord.Embed(title=f"Commands :", description=available_commands)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
    logger.info(f"Loaded !")
