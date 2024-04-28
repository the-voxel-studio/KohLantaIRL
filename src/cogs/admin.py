import typing
from os import name as os_name
from os import system

import discord
from discord import app_commands
from discord.ext import commands

from config.values import (  # OBLIGATOIRES (utilisation de la fonction eval)
    CHANNEL_ID_BOT_LOGS, COLOR_GREEN, COLOR_ORANGE, COLOR_RED)
from utils.control import is_admin
from utils.log import send_log, send_logs_file
from utils.logging import get_logger

from database.player import PlayerList

logger = get_logger(__name__)

COLOR_ORANGE, COLOR_RED


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='send', description='Envoyer un message depuis Denis Brogniart'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def send(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        content: str,
        color: typing.Literal['green', 'orange', 'red'],
    ):

        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        logger.info(
            f'Important message sending | Requested by {interaction.user} (id:{interaction.user.id}) | Channel id: {channel.id} | Color: {color} | Content: {content}'
        )
        self.embed = discord.Embed(
            title=content,
            color=eval('COLOR_' + color.upper()),
        )
        self.embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.avatar.url
        )
        self.embed.set_footer(text='Ce message est envoyé par un administrateur.')
        await channel.send(embed=self.embed)
        await interaction.response.send_message(
            content=f'Message envoyé dans <#{channel.id}>'
        )

    @app_commands.command(
        name='reboot', description='Redémarre le serveur de Denis Brogniart'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def reboot(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        if os_name == 'posix':
            logger.info(
                f'Preparing for manual reboot. | Requested by {interaction.user} (id:{interaction.user.id})'
            )
            await send_log(
                'Redémarrage manuel en cours',
                f'by **{interaction.user.display_name}**',
                color='orange',
            )
            logger.info('Ready to reboot.')
            system('sudo reboot')
        else:
            logger.error(
                f'Manual reboot is only possible on posix server | Requested by {interaction.user} (id:{interaction.user.id})'
            )

    @app_commands.command(
        name='shutdown', description='Eteind le serveur de Denis Brogniart'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def shutdown(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])
        if os_name == 'posix':
            logger.info(
                f'Preparing for shutdown. | Requested by {interaction.user} (id:{interaction.user.id})'
            )
            await send_log(
                'Extinction manuelle en cours',
                f'by **{interaction.user.display_name}**',
                color='orange',
            )
            logger.info('Ready to shutdown.')
            system('sudo halt')
        else:
            logger.error(
                f'Manual shutdown is only possible on posix server | Requested by {interaction.user} (id:{interaction.user.id})'
            )

    @app_commands.command(name='logs', description='To receive the bot.log file.')
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def logs(self, interaction: discord.Interaction):
        logger.info(
            f'Send Logs File > start | requested by: {interaction.user} (id:{interaction.user.id})'
        )
        await interaction.response.defer()
        await send_logs_file()
        self.embed = discord.Embed(
            title=':robot: Logs disponibles :moyai:',
            description=f':file_folder: Le fichier contenant mes logs est disponible dans ce channel: <#{CHANNEL_ID_BOT_LOGS}>.',
            color=COLOR_GREEN,
        )
        self.embed.set_footer(
            text='Ce fichier est strictement confidentiel et son accès est réservé aux administrateurs du serveur.'
        )
        await interaction.followup.send(embed=self.embed)
        logger.info(
            f'Send Logs File > OK | requested by: {interaction.user} (id:{interaction.user.id})'
        )

    @app_commands.command(
        name='clear', description='Supprimer un certain nombre de messages'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        logger.info(
            f'Partial channel clearing | Requested by {interaction.user} (id:{interaction.user.id}) | Number: {amount} | Channel id: {interaction.channel.id}'
        )
        await interaction.channel.purge(limit=amount)

    @app_commands.command(name='ping', description='To verify bot connection')
    @app_commands.default_permissions(manage_messages=True)
    async def ping(self, interaction: discord.Interaction):
        logger.info(
            f'Ping-Pong | requested by: {interaction.user} (id:{interaction.user.id})'
        )
        await interaction.response.send_message(
            'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDIwZWNoNnJ1ZW9nbDlhZjJjcTFtM215amYybmowYmc5YXZibW1uZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LnEuA5N3iZmFiDWP1n/giphy.gif'
        )

    @app_commands.command(
        name='tree_sync',
        description="Force la synchronisation de l'arbre des commandes",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def tree_sync(self, interaction: discord.Interaction):
        logger.info(
            f'Bot tree synchronisation > start | Requested by {interaction.user} (id:{interaction.user.id})'
        )
        await interaction.response.defer()
        synced = await self.bot.tree.sync()
        commands_list = [el.name for el in synced]
        self.embed = discord.Embed(
            title=':robot: Arbre synchronisé :moyai:',
            description=f':file_folder: Les commandes suivantes ont étés trouvées: {commands_list}',
            color=COLOR_GREEN,
        )
        self.embed.set_footer(
            text='Cette liste est strictement confidentielle et son accès est réservé aux administrateurs du serveur.'
        )
        await interaction.followup.send(embed=self.embed)
        logger.info(
            f'Bot tree synchronisation > OK | Requested by {interaction.user} (id:{interaction.user.id}) | Commands: {commands_list}'
        )

    @app_commands.command(
        name='player_infos',
        description='Affiche les infos des joueurs'
    )
    @app_commands.default_permissions(manage_messages=True)
    async def player_infos(self, interaction: discord.Interaction):
        logger.info(
            f'Player infos | Requested by {interaction.user} (id:{interaction.user.id})'
        )
        players = PlayerList()
        self.embed = discord.Embed(
            title=':robot: Informations joueurs :moyai:',
            description=f'Informations sans spoil sur les joueurs.\nNombre de joueurs: **{len(players.objects)}**',
            color=COLOR_GREEN,
        )
        for player in players.objects:
            self.embed.add_field(
                name=f':bust_in_silhouette: {player.object.nickname}',
                value=f"""
                    - Discord: <@{player.object.id}>
                    \n- Id: `{player.object.id}`
                    \n- Vivant: {':white_check_mark:' if player.object.alive else ':cross_mark:'}
                    \n- Lettre: `{player.object.letter if player.object.letter else 'N/A'}`
                    \n- Conseil d'élimination: `{player.object.death_council_number}`
                    \n- Dernier souhait exprimé: {':white_check_mark:' if player.object.last_wish_expressed else ':cross_mark:'}
                """,
                inline=False
            )
        self.embed.set_footer(
            text='Cette liste est strictement confidentielle et son accès est réservé aux administrateurs du serveur.'
        )
        await interaction.response.send_message(embed=self.embed)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
    logger.info('Loaded !')
