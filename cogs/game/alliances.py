import discord
from discord import app_commands
from discord.ext import commands

from config.values import (CATEGORIE_ID_ALLIANCES,
                           CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER, COLOR_GREEN,
                           COLOR_ORANGE, GUILD_ID)
from utils.bot import bot
from utils.logging import get_logger
from utils.models import Alliance, NewAlliance, Player

logger = get_logger(__name__)

class AlliancesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def alliance(self, ctx, *args):
        if ctx.message.guild: await ctx.message.delete()
        player = Player(id=ctx.author.id)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            logger.warning(f"PrivateMessage | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: /alliance")
            embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Impossible d'effectuer l'action demandée : la commande *alliance* est disponible seulement en message privé avec le robot (ici).", color=COLOR_ORANGE)
            await ctx.author.send(embed=embed)
        elif not player.alive:
            logger.warning(f"EliminatedPlayer | Sent by {ctx.author} (id:{ctx.author.id}) | Attempted to use the command: /alliance")
            embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Impossible d'effectuer l'action demandée : les joueurs éliminés ne peuvent pas créer d'alliance.", color=COLOR_ORANGE)
            await ctx.author.send(embed=embed)
        else:
            logger.info(f"New alliance creation started | Requested by {ctx.author} (id:{ctx.author.id}).")
            general_guild = bot.get_guild(GUILD_ID)
            guild = discord.utils.get(general_guild.categories, id=CATEGORIE_ID_ALLIANCES)
            channel_name = args[0] if args[0] else "new_alliance"
            overwrites = {
                general_guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
            }
            new_text_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
            new_voice_channel = await guild.create_voice_channel(channel_name, overwrites=overwrites)
            new_alliance = NewAlliance()
            new_alliance.text_id = new_text_channel.id
            new_alliance.voice_id = new_voice_channel.id
            new_alliance.name = channel_name
            new_alliance.creator = player._id
            new_alliance.save()
            embed=discord.Embed(title=f":robot: Nouvelle alliance :moyai:", description=f":white_check_mark: L'alliance {channel_name} a bien été créée : rendez-vous ici <#{new_text_channel.id}> pour y ajouter des joueurs.", color=COLOR_GREEN)
            await ctx.author.send(embed=embed)
            logger.info(f"New Alliance created | Requested by {ctx.author} (id:{ctx.author.id}) | Alliance text channel id: {new_text_channel.id}")

    @app_commands.command(name = "ajouter", description = "Ajouter un membre à une alliance")
    @app_commands.describe(
        prenom='Prénom du membre',
        initiale='Initiale du nom de famille du membre'
    )
    async def ajouter(self, interaction : discord.Interaction, prenom : str, initiale: str):
        logger.info(f"New alliance member addition started | Requested by {interaction.user} (id:{interaction.user.id}) | Alliance text channel id: {interaction.channel.id}")
        await interaction.response.defer()
        name = f"{prenom} {initiale}"
        player = Player(nickname=name)
        if player.id != 0:
            if player.alive:
                user = bot.get_user(player.id)
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
                embed=discord.Embed(title=f":robot: Nouveau membre :moyai:", description=f":new: <@{interaction.user.id}> a ajouté <@{player.id}> à l'alliance !", color=COLOR_GREEN)
                await interaction.followup.send(embed=embed)
                logger.info(f"New alliance member added | Requested by {interaction.user} (id:{interaction.user.id}) | New member: {player} (id:{player.id}) | Alliance text channel id: {interaction.channel.id}")
            else:
                logger.warning(f"NewAllianceMemberNotAlive | Requested by {interaction.user} (id:{interaction.user.id}) | New member: {player} (id:{player.id}) | Alliance text channel id: {interaction.channel.id}")
                embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Le joueur spécifié a été éliminé lors d'un vote, il est donc impossible de l'ajouter à une alliance.", color=COLOR_ORANGE)
                await interaction.followup.send(embed=embed)
        else:
            logger.warning(f"NewAllianceMemberNotFound | Requested by {interaction.user} (id:{interaction.user.id}) | New member list: {[prenom,initiale]} | Alliance text channel id: {interaction.channel.id}")
            embed=discord.Embed(title=f":robot: Action impossible :moyai:", description=f":warning: Le joueur spécifié est introuvable. Veuillez vérifier le fonctionnement de cette commande ici <#{CHANNEL_ID_HELP_ALLIANCE_ADD_PLAYER}>", color=COLOR_ORANGE)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name = "supprimer", description = "Supprimer un membre d'une alliance")
    async def supprimer(self, interaction: discord.Interaction, member: discord.Member):
        logger.info(f"Alliance member removing started | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id}) | Alliance text channel id: {interaction.channel.id}")
        await interaction.response.defer()
        player = Player(id=member.id)
        alliance = Alliance(text_id=interaction.channel.id)
        await interaction.channel.set_permissions(member, overwrite=None)
        await bot.get_channel(alliance.voice_id).set_permissions(member, overwrite=None)
        alliance.remove_member(player._id)
        embed=discord.Embed(title=f":robot: Expulsion d'une alliance :moyai:", description=f":warning: Vous avez été supprimé de l'alliance *{interaction.channel.name}* par <@{interaction.user.id}> !", color=COLOR_ORANGE)
        await member.send(embed=embed)
        embed=discord.Embed(title=f":robot: Expulsion :moyai:", description=f":warning: <@{interaction.user.id}> a supprimé <@{player.id}> de l'alliance !", color=COLOR_ORANGE)
        await interaction.followup.send(embed=embed)
        logger.info(f"Alliance member removed | Requested by {interaction.user} (id:{interaction.user.id}) | Member: {member} (id:{member.id}) | Alliance text channel id: {interaction.channel.id}")



async def setup(bot):
    await bot.add_cog(AlliancesCog(bot))
    logger.info(f"Loaded !")