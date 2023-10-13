from discord.ext import commands
from discord import app_commands
import discord
from utils.logging import get_logger
from utils.bot import bot
import random

logger = get_logger(__name__)

class AlliancesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "help", description="Commands infos")   
    async def help(self, interaction: discord.Interaction, command:str=None):
        if command is not None:
            for c in bot.tree.get_commands():
                if c.name == command:
                    command=c
                    break
                else:
                    continue
            try:
                txt=command.description
                embed = discord.Embed(title=command.name,description=txt)
                await interaction.response.send_message(embed=embed)
            except AttributeError: #command not found
                e = discord.Embed(title="Error:",description=f"Command {command} not found", color=0xFF0000)
                await interaction.response.send_message(embed=e)
            return
        names = [f"{command.name} : {command.description}" for command in bot.tree.get_commands()] 
        available_commands = "\n".join(names)
        embed = discord.Embed(title=f"Commands ({len(names)}):",description=available_commands)
        embed.set_footer(text=f"  /help <command> (e.g /help {random.choice(names)})")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AlliancesCog(bot))
    logger.info(f"Loaded !")