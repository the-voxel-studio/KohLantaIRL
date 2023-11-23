import typing
from os import system

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View

from utils.logging import get_logger
from config.values import CHANNEL_ID_HELP_ALLIANCE, COLOR_GREEN

logger = get_logger(__name__)

class HowToCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class AllianceView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Créer une nouvelle alliance", style=discord.ButtonStyle.primary, emoji="😎")
        async def button_callback(self, interaction, button):
            await interaction.response.send_message(content="You clicked the button!",ephemeral=True)

    @app_commands.command(name = "howto-alliances", description = "Crée le How-To des alliances")
    # @app_commands.default_permissions(create_instant_invite=True)
    async def howto_alliances(self, interaction: discord.Interaction):
        self.channel = self.bot.get_channel(CHANNEL_ID_HELP_ALLIANCE)
        # self.content = "## Créer une alliance:\nPour cela, il est nécessaire d'envoyer un message directement au robot <@1139673903678095400> en message privé sous la forme suivante:\n\n**/alliance \"nom-de-l-alliance\"**\n\nL'expression \"nom-de-l-alliance\" est à remplacer par ce que vous souhaitez, le reste doit être recopié tel-quel.\nL'expression remplaçant \"nom-de-l-alliance\" ne peut pas contenir d'espace ou de caractère spécial autre que \"-\".\nIl est impératif de communiquer avec le robot en discussion privée car dans le cas contraire, cela enverra une notification à tous les joueurs annonçant que vous créez une alliance et son nom.\n## Ajouter un membre à l'alliance:\n**/ajouter <@906850747654758430>**\nL'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez ajouter.\n## Supprimer un membre de l'alliance:\n**/supprimer <@906850747654758430>**\nL'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez ajouter."
        self.content = "## Renommer l'alliance:\n**/nom \"nouveau-nom-de-l-alliance\"**\nL'expression \"nouveau-nom-de-l-alliance\" est à remplacer par le nouveau nom que vous souhaitez définir.\n## Ajouter un membre à l'alliance:\n**/ajouter <@906850747654758430>**\nL'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez ajouter.\n## Supprimer un membre de l'alliance:\n**/supprimer <@906850747654758430>**\nL'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez ajouter.\n## Créer un alliance:\nCliquez sur le bouton ci-dessous."
        # self.view = View(timeout=None)
        # self.btn1 = Button(style=ButtonStyle.primary,label="Créer une nouvelle alliance")
        # self.view.add_item(self.btn1)
        self.view = self.AllianceView()
        await self.channel.send(self.content,view=self.view)
        embed=discord.Embed(title=f":robot: Message d'aide généré :moyai:", color=COLOR_GREEN)
        await interaction.response.send_message(embed=embed)
        # TODO save how-to msg id in db
        # TODO modify message callback each restart

async def setup(bot):
    await bot.add_cog(HowToCog(bot))
    logger.info(f"Loaded !")