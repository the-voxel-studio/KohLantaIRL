import datetime
import typing

import discord
from discord import app_commands
from discord.ext import commands

import utils.game.votes as vote
from config.values import CHANNEL_ID_GENERAL, COLOR_GREEN, COLOR_ORANGE
from database.votelog import VoteLog
from utils.bot import bot
from utils.control import is_admin
from utils.logging import get_logger

logger = get_logger(__name__)


class VotesCog(commands.Cog):
    """Votes commands cog."""

    def __init__(self, bot):
        """Init the cog."""

        self.bot = bot

    @app_commands.command(name='open_vote', description="Ouverture d'un nouveau vote")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def open_vote(self, interaction: discord.Interaction):
        """Open a new vote."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Vote opening | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await interaction.response.defer()
        await vote.open(interaction)

    @app_commands.command(name='close_vote', description='Fermeture du vote en cours')
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def close_vote(self, interaction: discord.Interaction):
        """Close the current vote."""

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Vote closing | Requested by {interaction.user} (id:{interaction.user.id}).'
        )
        await interaction.response.defer()
        await vote.close(interaction)

    @app_commands.command(
        name='eliminate',
        description='Elimine un joueur',
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def eliminate(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: typing.Literal['After equality', 'Other reason'],
    ):
        """Eliminate a player."""

        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Member elimination started | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )
        await vote.eliminate(interaction, member, reason)
        logger.info(
            f'Member eliminated | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )

    @app_commands.command(
        name='resurrect', description='Réintroduit un joueur dans la partie.'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def resurrect(self, interaction: discord.Interaction, member: discord.Member):
        """Resurrect a player."""

        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Member resurrection start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )
        await vote.resurrect(interaction, member)
        logger.info(
            f'Member resurrection OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )

    @app_commands.command(
        name='set_finalist', description='Définir un joueur comme finaliste.'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def set_finalise(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Set a player as finalist."""

        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Member set to finalist start | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )
        await vote.set_finalist(interaction, member)
        logger.info(
            f'Member set to finalist OK | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )

    @app_commands.command(name='dv', description='Dernière volonté. (uniquement en mp)')
    @app_commands.describe(contenu='Contenu du message à envoyer')
    async def last_volontee(self, interaction: discord.Interaction, contenu: str):
        """Last volontee."""

        # TODO modify with multiple eliminated after a unique vote
        await interaction.response.defer(ephemeral=True)
        if isinstance(interaction.channel, discord.DMChannel):
            vote_log = VoteLog(last=True)
            vote_date = datetime.datetime.strptime(vote_log.object.date, '%d/%m/%Y %H:%M:%S')
            actual_date = datetime.datetime.now()
            max_date = (vote_date + datetime.timedelta(days=1)).replace(
                hour=21, minute=0, second=0, microsecond=0
            )
            not_timeout = actual_date <= max_date
            eliminated_list = [
                i
                for i, el in enumerate(vote_log.object.eliminated)
                if el.id == interaction.user.id
            ]
            try:
                eliminated = vote_log.object.eliminated.objects[eliminated_list[0]]
                is_last_eliminate = True
            except IndexError:
                is_last_eliminate = False
            if is_last_eliminate and not_timeout:
                type(eliminated)
                eliminated.find()
                if not eliminated.last_wish_expressed:
                    logger.info(
                        f'Last wish > start | Requested by {interaction.user} (id:{interaction.user.id}) | Content: {contenu}'
                    )
                    eliminated.express_last_wish()
                    embed = discord.Embed(
                        description=contenu,
                        color=COLOR_GREEN,
                    )
                    self.embed.set_author(
                        name=f'{interaction.user.display_name} : Dernière volontée',
                        icon_url=interaction.user.avatar.url
                    )
                    embed.set_footer(
                        text="Les administrateurs ne sont pas responsables des propos tenus dans ce message. Si vous trouvez un contenu inapproprié ou problématique, n'hésitez pas à le signaler en message privé."
                    )
                    await bot.get_channel(CHANNEL_ID_GENERAL).send(embed=embed)
                    embed = discord.Embed(
                        title=':robot: Ta dernière volonté a été exprimée :moyai:',
                        description=f'Vous pouvez la voir ici <#{CHANNEL_ID_GENERAL}>',
                        color=COLOR_GREEN,
                    )
                    await interaction.followup.send(embed=embed)
                    logger.info(
                        f'Last wish > OK | Requested by {interaction.user.name} (id:{interaction.user.id}) | Content: {contenu}'
                    )
                else:
                    embed = discord.Embed(
                        title=':robot: Commande verrouillée :moyai:',
                        description=':no_entry: Cette commande a déjà été utilisée.\n\nCommande : /dv',
                        color=COLOR_ORANGE,
                    )
                    embed.set_footer(
                        text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
                    )
                    await interaction.followup.send(embed=embed)
            else:
                raise commands.errors.MissingPermissions(['LastWich'])
        else:
            embed = discord.Embed(
                title=':robot: Commande privée :moyai:',
                description=':no_entry: Cette commande est seulement disponible en message privé.\n\nCommande : /dv',
                color=COLOR_ORANGE,
            )
            embed.set_footer(
                text="Essayer à plusieurs reprises d'utiliser une commande interdite ou y parvenir sans autorisation des administrateurs entrainera systématiquement un bannissement temporaire ou définitif du joueur."
            )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    """Setup the cog."""

    await bot.add_cog(VotesCog(bot))
    logger.info('Loaded !')
