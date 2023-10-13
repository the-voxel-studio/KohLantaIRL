from discord.ext import commands
from discord import app_commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="test slash command")
    async def hello(self, ctx):
        await ctx.send("Hello from MyCog!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))