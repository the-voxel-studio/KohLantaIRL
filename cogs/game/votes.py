import typing

import discord
from discord import app_commands
from discord.ext import commands

import utils.game.votes as vote
from config.values import COLOR_GREEN, COLOR_ORANGE, CHANNEL_ID_GENERAL
from utils.bot import bot
from utils.control import is_admin
from utils.logging import get_logger
from utils.models import VoteLog
import datetime

logger = get_logger(__name__)

class VotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "open_vote", description = "Ouverture d'un nouveau vote")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def open_vote(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Vote opening | Requested by {interaction.user} (id:{interaction.user.id}).")
        await interaction.response.defer()
        await vote.open(interaction)

    @app_commands.command(name = "close_vote", description = "Fermeture du vote en cours")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def close_vote(self, interaction: discord.Interaction): 
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Vote closing | Requested by {interaction.user} (id:{interaction.user.id}).")
        await interaction.response.defer()
        await vote.close(interaction)

    @app_commands.command(name = "eliminate", description = "Elimine un joueur après le choix du dernier éliminé")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def eliminate(self, interaction: discord.Interaction, member: discord.Member, reason: typing.Literal["After equality","Other reason"]):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member elimination started | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.eliminate(interaction,member,reason)
        logger.info(f"Member eliminated | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

    @app_commands.command(name = "resurrect", description = "Réintroduit un joueur dans la partie.")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def resurrect(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member resurrection start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.resurrect(interaction,member)
        logger.info(f"Member resurrection OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

    @app_commands.command(name = "set_finalist", description = "Définir un joueur comme finaliste.")
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def set_finalise(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(["Admin"])
        logger.info(f"Member set to finalist start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")
        await vote.set_finalist(interaction,member)
        logger.info(f"Member set to finalist OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})")

    @app_commands.command(name = "dv", description = "Dernière volonté. (uniquement en mp)")
    @app_commands.describe(contenu="Contenu du message à envoyer")
    async def last_volontee(self, interaction: discord.Interaction, contenu: str):
        # CHECK limit last wich to one per eliminate
        # TODO modify with multiple eliminated after a unique vote
        await interaction.response.defer(ephemeral=True)
        if isinstance(interaction.channel, discord.DMChannel):
            vote_log = VoteLog(last=True)
            vote_date = datetime.datetime.strptime(vote_log.date, "%d/%m/%Y %H:%M:%S")
            actual_date = datetime.datetime.now()
            # CHECK change to 21h the day after the vote
            max_date = (vote_date + datetime.timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
            not_timeout = actual_date <= max_date
            is_last_eliminate = vote_log.eliminated.id == interaction.user.id
            if is_last_eliminate and not_timeout:
                if not vote_log.eliminated.last_wich_expressed:
                    logger.info(f"Last wish > start | Requested by {interaction.user} (id:{interaction.user.id}) | Content: {contenu}")
                    vote_log.eliminated.express_last_wish()
                    embed=discord.Embed(title=f":robot: Dernière volonté de {interaction.user} :moyai:", description=f"**{contenu}**", color=COLOR_GREEN)
                    embed.set_footer(text="Les administrateurs ne sont pas responsables des propos tenus dans ce message. Si vous trouvez un contenu inapproprié ou problématique, n'hésitez pas à le signaler en message privé.")
                    await bot.get_channel(CHANNEL_ID_GENERAL).send(embed=embed)
                    embed=discord.Embed(title=":robot: Ta dernière volonté a été exprimée :moyai:", description=f"Vous pouvez la voir ici <#{CHANNEL_ID_GENERAL}>", color=COLOR_GREEN)
                    await interaction.followup.send(embed=embed)
                    logger.info(f"Last wish > OK | Requested by {interaction.user.name} (id:{interaction.user.id}) | Content: {contenu}")
                else:
                    embed=discord.Embed(title=f":robot: Commande verrouillée :moyai:", description=f":no_entry: Cette commande a déjà été utilisée.\n\nCommande : /dv", color=COLOR_ORANGE)
                    embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
                    await interaction.followup.send(embed=embed)
            else:
                raise commands.errors.MissingPermissions("LastWich")
        else:
            embed=discord.Embed(title=f":robot: Commande privée :moyai:", description=f":no_entry: Cette commande est seulement disponible en message privé.\n\nCommande : /dv", color=COLOR_ORANGE)
            embed.set_footer(text=f"Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur.")
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VotesCog(bot))
    logger.info(f"Loaded !")