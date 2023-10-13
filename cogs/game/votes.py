from discord.ext import commands
from discord import app_commands
import discord
from utils.logging import get_logger
from config.values import GUILD_ID, CHANNEL_ID_RESULTATS
from utils.models import Player
from utils.bot import bot
import utils.game.votes as vote

logger = get_logger(__name__)

class VotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "open_vote", description = "Ouverture d'un nouveau vote")
    async def open_vote(self, interaction: discord.Interaction):
        logger.info(f"Vote opening | Requested by {interaction.user} (id:{interaction.user.id}).")
        await interaction.response.defer()
        await vote.open(interaction)

    @app_commands.command(name = "close_vote", description = "Fermeture du vote en cours")
    async def close_vote(self, interaction: discord.Interaction): 
        logger.info(f"Vote closing | Requested by {interaction.user} (id:{interaction.user.id}).")
        await interaction.response.defer()
        await vote.close(interaction)

    @app_commands.command(name = "eliminate", description = "Elimine un joueur après le choix du dernier éliminé")
    async def eliminate(self, interaction: discord.Interaction, member: discord.Member):
        logger.info(f"Member elimination started | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        self.eliminated = Player(id=member.id)
        self.players = Player(option="living")
        self.players_list = self.players.list
        self.embed = discord.Embed(
            title=f"**{self.eliminated.nickname}**",
            description=f"Le dernier éliminé a décidé de l'éliminer et sa sentence est irrévocable !",
            color=15548997
        )
        self.embed.set_author(name="Résultat du conseil",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCJB81hLY3rg1pIqRNsLkbeQ8VXe_-kSOjPk5PDz5SRmBCrCDqMxiRSmciGu3z3IuQdZY&usqp=CAUp")
        self.embed.set_thumbnail(url="https://cache.cosmopolitan.fr/data/photo/w2000_ci/52/koh-elimnation.webp")
        self.embed.add_field(name=f"Cet aventurier a reçu le vote du dernier éliminé suite à une égalité.", value=f"Il reste {len(self.players_list)-1} aventuriers en jeu.", inline=True)
        channel = bot.get_channel(CHANNEL_ID_RESULTATS)
        await channel.send(embed=self.embed)
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(self.eliminated.id)
        role = discord.utils.get(guild.roles, name="Joueur")
        new_role = discord.utils.get(guild.roles, name="Eliminé")
        await member.remove_roles(role)
        await member.add_roles(new_role)
        self.eliminated.eliminate()
        logger.info(f"Member eliminated | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

async def setup(bot):
    await bot.add_cog(VotesCog(bot))
    logger.info(f"Loaded !")