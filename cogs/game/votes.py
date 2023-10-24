import typing

import discord
from discord import app_commands
from discord.ext import commands

import utils.game.votes as vote
from config.values import CHANNEL_ID_RESULTATS, COLOR_GREEN, GUILD_ID
from utils.bot import bot
from utils.control import is_admin
from utils.logging import get_logger
from utils.models import Player

logger = get_logger(__name__)

class VotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "open_vote", description = "Ouverture d'un nouveau vote")
    @app_commands.default_permissions(create_instant_invite=True)
    async def open_vote(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Vote opening | Requested by {interaction.user} (id:{interaction.user.id}).")
        await interaction.response.defer()
        await vote.open(interaction)

    @app_commands.command(name = "close_vote", description = "Fermeture du vote en cours")
    @app_commands.default_permissions(create_instant_invite=True)
    async def close_vote(self, interaction: discord.Interaction): 
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Vote closing | Requested by {interaction.user} (id:{interaction.user.id}).")
        await interaction.response.defer()
        await vote.close(interaction)

    @app_commands.command(name = "eliminate", description = "Elimine un joueur après le choix du dernier éliminé")
    @app_commands.default_permissions(moderate_members=True)
    async def eliminate(self, interaction: discord.Interaction, member: discord.Member, reason: typing.Literal["After equality","Other reason"]):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member elimination started | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.eliminate(interaction,member,reason)
        logger.info(f"Member eliminated | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

    @app_commands.command(name = "resurrect", description = "Réintroduit un joueur dans la partie.")
    @app_commands.default_permissions(moderate_members=True)
    async def resurrect(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member resurrection start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.resurrect(interaction,member)
        logger.info(f"Member resurrection OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

    @app_commands.command(name = "set_finalist", description = "Définir un joueur comme finaliste.")
    @app_commands.default_permissions(moderate_members=True)
    async def set_finalise(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member set to finalist start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.set_finalist(interaction,member)
        logger.info(f"Member set to finalist OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

    @app_commands.command(name = "dv", description = "Définir un joueur comme finaliste.")
    @app_commands.default_permissions(moderate_members=True)
    async def last_volontee(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member set to finalist start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.set_finalist(interaction,member)
        logger.info(f"Member set to finalist OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

async def setup(bot):
    await bot.add_cog(VotesCog(bot))
    logger.info(f"Loaded !")