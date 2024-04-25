import typing

import discord
from discord import app_commands
from discord.ext import commands

from config.values import CHANNEL_ID_BOT, COLOR_GREEN
from utils.control import is_admin
from utils.logging import get_logger
from utils.punishments import timeout

logger = get_logger(__name__)


class MutingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='mute', description='Rendre muet un membre')
    @app_commands.guild_only()
    @app_commands.describe(
        member='The member to mute',
        timedelta='The time of the punishment',
        reason='The reason of the punishment',
    )
    @app_commands.default_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        timedelta: typing.Literal['30s', '60s', '10min', '1h', '12h', '1j', '2j'],
        reason: str = None,
    ):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Member muting | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )
        await interaction.response.defer()
        match timedelta:
            case '30s':
                self.minutes = 0.5
            case '60s':
                self.minutes = 1
            case '10min':
                self.minutes = 10
            case '1h':
                self.minutes = 60
            case '12h':
                self.minutes = 720
            case '1j':
                self.minutes = 1440
            case '2j':
                self.minutes = 2880
            case _:
                self.minutes = 10
        await timeout(
            member,
            author=interaction.user,
            minutes=self.minutes,
            reason=reason,
            interaction=interaction,
        )

    @app_commands.command(name='unmute', description='Rendre la parole à un membre')
    @app_commands.guild_only()
    @app_commands.describe(member='The member to unmute')
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Member unmuting | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id})'
        )
        await member.timeout(None)
        self.embed = discord.Embed(
            title=f':robot: {member} Unmuted :moyai:',
            description=f'by **{interaction.user}**',
            color=COLOR_GREEN,
        )
        await self.bot.get_channel(CHANNEL_ID_BOT).send(embed=self.embed)
        await interaction.response.send_message(embed=self.embed)


async def setup(bot):
    await bot.add_cog(MutingCog(bot))
    logger.info('Loaded !')
