import discord
from discord import app_commands
from discord.ext import commands

from config.values import (COLOR_GREEN, COLOR_ORANGE)
from utils.bot import bot
from utils.logging import get_logger
from utils.models import Alliance, Player
from utils.game.alliances import close_alliance

from bson.objectid import ObjectId

logger = get_logger(__name__)

class AlliancesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def id_renamed(self,interaction: discord.Interaction):
        self.first_name = "new_channel_"+"_".join(interaction.user.nick.lower().split(" "))
        return interaction.channel.name != self.first_name

    @app_commands.command(name = "nom", description = "Renommer une alliance")
    @app_commands.guild_only()
    async def rename(self, interaction: discord.Interaction, nouveau_nom: str):
        logger.info(f"Alliance renaming > start | Requested by {interaction.user} (id:{interaction.user.id}) | New name: {nouveau_nom} | Alliance text channel id: {interaction.channel.id}")
        await interaction.response.defer()
        alliance = Alliance(text_id=interaction.channel.id)
        voice_channel = bot.get_channel(alliance.voice_id)
        await interaction.channel.edit(name=nouveau_nom)
        await voice_channel.edit(name=nouveau_nom)
        logger.info(f"Alliance renaming > OK | Requested by {interaction.user} (id:{interaction.user.id}) | New name: {nouveau_nom} | Alliance text channel id: {interaction.channel.id}")
        embed=discord.Embed(title=f":robot: Alliance renommée :moyai:", color=COLOR_GREEN)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name = "ajouter", description = "Ajouter un membre à une alliance")
    @app_commands.guild_only()
    async def ajouter(self, interaction : discord.Interaction, user: discord.Member):
        logger.info(f"New alliance member addition started | Requested by {interaction.user} (id:{interaction.user.id}) | Alliance text channel id: {interaction.channel.id}")
        await interaction.response.defer()
        player = Player(id=user.id)
        if not await self.id_renamed(interaction):
            logger.warning(f"NewAllianceNotRenamed | Requested by {interaction.user} (id:{interaction.user.id}) | New member: {player} (id:{user.id}) | Alliance text channel id: {interaction.channel.id}")
            embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: **Vous devez tout d'abord renommer l'alliance !**", color=COLOR_ORANGE)
            embed.add_field(name="Comment faire ?", value="Il suffit d'utiliser la commande `/nom` dans le champ de texte ci-desous. Tapez simplement / et la commande vous  sera proposée.")
            await interaction.followup.send(embed=embed)
        elif player.alive:
            alliance = Alliance(text_id=interaction.channel.id)
            perms = interaction.channel.overwrites_for(user)
            perms.read_messages = True
            await interaction.channel.set_permissions(user, overwrite=perms)
            voice_channel = bot.get_channel(alliance.voice_id)
            perms = voice_channel.overwrites_for(user)
            perms.read_messages = True
            await voice_channel.set_permissions(user, overwrite=perms)
            alliance.add_member(player._id)
            embed=discord.Embed(title=f":robot: Nouvelle alliance :moyai:", description=f":new: Vous avez été ajouté à l'alliance <#{interaction.channel.id}> par <@{interaction.user.id}> !", color=COLOR_GREEN)
            await user.send(embed=embed)
            embed=discord.Embed(title=f":robot: Nouveau membre :moyai:", description=f":new: <@{interaction.user.id}> a ajouté <@{user.id}> à l'alliance !", color=COLOR_GREEN)
            await interaction.followup.send(embed=embed)
            logger.info(f"New alliance member added | Requested by {interaction.user} (id:{interaction.user.id}) | New member: {player} (id:{user.id}) | Alliance text channel id: {interaction.channel.id}")
        
        else:
            logger.warning(f"NewAllianceMemberNotAlive | Requested by {interaction.user} (id:{interaction.user.id}) | New member: {player} (id:{user.id}) | Alliance text channel id: {interaction.channel.id}")
            embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Le joueur spécifié a été éliminé lors d'un vote, il est donc impossible de l'ajouter à une alliance.", color=COLOR_ORANGE)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name = "dissoudre", description = "Dissoudre une alliance")
    @app_commands.guild_only()
    async def dissolve(self, interaction : discord.Interaction):
        logger.info(f"Alliance dissolution > start | Requested by {interaction.user} (id:{interaction.user.id}) | Alliance text channel id: {interaction.channel.id}")
        await interaction.response.defer()
        await close_alliance(interaction.channel.id,interaction.user)

    @app_commands.command(name = "expulser", description = "Supprimer un membre d'une alliance")
    @app_commands.guild_only()
    async def expulser(self, interaction: discord.Interaction, member: discord.Member):
        logger.info(f"Alliance member removing started | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id}) | Alliance text channel id: {interaction.channel.id}")
        await interaction.response.defer()
        player = Player(id=member.id)
        alliance = Alliance(text_id=interaction.channel.id)
        await interaction.channel.set_permissions(member, overwrite=None)
        await bot.get_channel(alliance.voice_id).set_permissions(member, overwrite=None)
        alliance.remove_member(player._id)
        embed=discord.Embed(title=f":robot: Expulsion d'une alliance :moyai:", description=f":warning: Vous avez été supprimé de l'alliance *{interaction.channel.name}* par <@{interaction.user.id}> !", color=COLOR_ORANGE)
        await member.send(embed=embed)
        embed=discord.Embed(title=f":robot: Expulsion :moyai:", description=f":warning: <@{interaction.user.id}> a supprimé <@{member.id}> de l'alliance !", color=COLOR_ORANGE)
        await interaction.followup.send(embed=embed)
        logger.info(f"Alliance member removed | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id}) | Alliance text channel id: {interaction.channel.id}")

async def setup(bot):
    await bot.add_cog(AlliancesCog(bot))
    logger.info(f"Loaded !")