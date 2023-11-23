import typing
from os import system

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View

from utils.logging import get_logger
from utils.models import Variables
from utils.game.alliances import new_alliance
from config.values import CHANNEL_ID_HELP_ALLIANCE, COLOR_GREEN
from utils.bot import bot

logger = get_logger(__name__)

class AllianceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Créer une nouvelle alliance", style=discord.ButtonStyle.primary, custom_id="new_alliance_btn")
    async def button_callback(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        await new_alliance(interaction)

class HowToCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @app_commands.command(name = "howto-alliances", description = "Crée le How-To des alliances")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def howto_alliances(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.channel = self.bot.get_channel(CHANNEL_ID_HELP_ALLIANCE)
        await self.channel.purge(limit=10)
        msg_list = [
            ["✏️ Renommer l'alliance:","/nom \"nouveau-nom-de-l-alliance\"","L'expression \"nouveau-nom-de-l-alliance\" est à remplacer par le nouveau nom que vous souhaitez définir."],
            ["🤝 Ajouter un membre à l'alliance:","/ajouter @Assistant de Denis","L'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez ajouter."],
            ["💔 Expulser un membre de l'alliance:","/expulser @Assistant de Denis","L'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez expulser."],
            ["🗑️ Dissoudre l'alliance:","/dissoudre","Cette commande est uniquement utilisable par le plus ancien membre de l'alliance."]
        ]
        for msg in msg_list:
            self.embed = embed=discord.Embed(title=msg[0])
            self.embed.add_field(name=msg[1], value=msg[2])
            await self.channel.send(embed=self.embed)
        self.view = AllianceView()
        self.embed = embed=discord.Embed(title="🆕 Créer un alliance:", description="Cliquez sur le bouton ci-dessous.")
        self.msg = await self.channel.send(embed=self.embed,view=self.view)
        Variables.set_btn_how_to_alliance_msg_id(self.msg.id)
        embed=discord.Embed(title=f":robot: Message d'aide généré :moyai:", color=COLOR_GREEN)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HowToCog(bot))
    logger.info(f"Loaded !")