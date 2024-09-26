import discord
from discord import app_commands
from discord.ext import commands

from config.values import (CHANNEL_ID_HELP_ALLIANCE, CHANNEL_ID_INSCRIPTION,
                           COLOR_GREEN)
from database.game import Game
from utils.bot import bot
from utils.game.alliances import new_alliance
from utils.logging import get_logger


class AllianceView(discord.ui.View):
    """Alliance view."""

    def __init__(self):
        """Init the view."""

        super().__init__(timeout=None)

    @discord.ui.button(
        label='Créer une nouvelle alliance',
        style=discord.ButtonStyle.primary,
        custom_id='new_alliance_btn',
    )
    async def button_callback(self, interaction, button):
        """Button callback."""

        await interaction.response.defer(ephemeral=True)
        await new_alliance(interaction)


class HowToCog(commands.Cog):
    """How-To commands cog."""

    def __init__(self, bot):
        """Init the cog."""

        self.bot = bot

    @app_commands.command(
        name='howto-alliances', description='Crée le How-To des alliances'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def howto_alliances(self, interaction: discord.Interaction):
        """Create the How-To of alliances."""

        await interaction.response.defer()
        self.channel = self.bot.get_channel(CHANNEL_ID_HELP_ALLIANCE)
        await self.channel.purge(limit=10)
        msg_list = [
            [
                "✏️ Renommer l'alliance:",
                "/nom 'nouveau-nom-de-l-alliance'",
                "L'expression 'nouveau-nom-de-l-alliance' est à remplacer par le nouveau nom que vous souhaitez définir.",
            ],
            [
                "🤝 Ajouter un membre à l'alliance:",
                '/ajouter @Assistant de Denis',
                "L'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez ajouter."
            ],
            [
                "💔 Expulser un membre de l'alliance:",
                '/expulser @Assistant de Denis',
                "L'expression <@906850747654758430> est à remplacer par le joueur que vous souhaitez expulser."
            ],
            [
                "🗑️ Dissoudre l'alliance:",
                '/dissoudre',
                "Cette commande est uniquement utilisable par le plus ancien membre de l'alliance."
            ]
        ]
        for msg in msg_list:
            self.embed = embed = discord.Embed(title=msg[0])
            self.embed.add_field(name=msg[1], value=msg[2])
            await self.channel.send(embed=self.embed)
        self.view = AllianceView()
        self.embed = embed = discord.Embed(
            title='🆕 Créer un alliance:',
            description='Cliquez sur le bouton ci-dessous.'
        )
        self.msg = await self.channel.send(embed=self.embed, view=self.view)
        Game.btn_how_to_alliance_msg_id = self.msg.id
        embed = discord.Embed(
            title=":robot: Message d'aide généré :moyai:", color=COLOR_GREEN
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name='howto-joining',
        description="Crée le How-To de l'inscription"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def howto_joining(self, interaction: discord.Interaction):
        """Create the How-To of joining."""

        embed = discord.Embed(
            title='Vous souhaitez nous rejoindre ?',
            description='Vous pouvez dès à présent vous inscrire à la prochaine saison de KohLanta IRL !',
            color=0x109319,
        )
        embed.set_author(
            name='Inscription',
            icon_url='https://cdn.discordapp.com/avatars/1139673903678095400/fe3974836708aab020a743b2700e87e4.webp?size=100',
        )
        embed.set_thumbnail(
            url='https://photos.tf1.fr/1200/720/vignette-16-9-4d6adf-748cc7-0@1x.webp'
        )
        embed.add_field(
            name="Entrez votre prénom et l'initale de votre nom dans le champ ci-dessous.",
            value='Exemple : Arthur D',
            inline=False,
        )
        embed.add_field(
            name="Le prénom ne doit pas contenir d'espace ou de caractère spécial autre que '-'.",
            value="Vous avez un prénom composé ? Remplacez les espaces par un caractère '-'.",
            inline=False,
        )
        embed.set_footer(
            text='Vous rencontrez un problème ? Contactez dès que possible un administrateur.'
        )
        channel = bot.get_channel(CHANNEL_ID_INSCRIPTION)
        await channel.send(embed=embed)


async def setup(bot):
    """Setup the cog."""

    logger = get_logger(__name__)
    await bot.add_cog(HowToCog(bot))
    logger.debug('Loaded !')
