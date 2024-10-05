import discord
from discord import app_commands
from discord.ext import commands
from config.values import COLOR_GREEN, COLOR_ORANGE, COLOR_RED
from database.player import Player
from database.game import Game, RewardCategories, RewardCategoriesList, Reward
from utils.logging import get_logger
from utils.game.rewards.block import blocking_reward
from utils.game.rewards.mute import muting_reward
from utils.game.rewards.resurrect import resurrecting_reward
from utils.control import is_admin


logger = get_logger(__name__)


class RewardsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='pouvoir', description="Execution d'un pouvoir suite à une activité"
    )
    async def power(
        self,
        interaction: discord.Interaction,
        power: RewardCategories,
        target: discord.Member,
    ):
        """Execute the power won after an activity"""

        logger.info(
            f'Power execution | Requested by {interaction.user} (id:{interaction.user.id}) | power: {power} | target : {target.name} (id:{target.id})'
        )

        await interaction.response.defer()

        # CHECK verify if the user is alive
        # Checking if the user is alive
        # If it's not the case, the power can't be used
        player = Player(id=interaction.user.id)
        if not player.object.alive:
            # CHECK response
            logger.info(
                f'Power execution : not alive | Requested by {interaction.user} (id:{interaction.user.id}) | power: {power} | target : {target.name} (id:{target.id})'
            )
            await message_user_not_alive(interaction)
            return

        # CHECK verify not vote in progress
        # Verify that there is no vote in progress
        # If it's the case, the power can't be used
        if Game.vote_msg_id != 0:
            logger.warning(f'Power execution : abort : vote in progress | Requested by {interaction.user} (id:{interaction.user.id}) | power: {power} | target : {target.name} (id:{target.id})')
            await message_vote_in_progress(interaction, power)
            return

        player_powers = [
            reward.category
            for reward in Game.rewards
            if reward.player_id == player.object.id
        ]
        if power in player_powers:
            match power:
                case 'mute':
                    # CHECK mute the target
                    await muting_reward(interaction, interaction.user, player, target)
                case 'block':
                    # CHECK reward : block
                    await blocking_reward(interaction, interaction.user, player, target)
                case 'resurrect':
                    # CHECK resurrect the target
                    await resurrecting_reward(interaction, interaction.user, player, target)
                case _:
                    await message_not_an_executable_power(interaction, power)
        else:
            await message_you_dont_have_this_power(interaction, power)

    @app_commands.command(
        name='give_power', description="Ajout d'un pouvoir suite à une activité"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    async def give_reward(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reward: RewardCategories
    ):
        """Give the power won after an activity"""

        logger.info(
            f'Power Giving | Requested by {interaction.user} (id:{interaction.user.id}) | reward: {reward}'
        )

        await interaction.response.defer()
        if not is_admin(interaction.user):
            raise commands.MissingPermissions(['Admin'])

        if reward not in RewardCategoriesList:
            raise ValueError(f'Invalid reward category: {reward}')
        Game.add_reward(Reward(user.id, reward))

        await message_give_reward_success_to_recipient(interaction, user, reward)
        await message_give_reward_success_to_giver(interaction, user, reward)


async def message_give_reward_success_to_giver(
        interaction: discord.Interaction,
        user: discord.Member,
        reward: Reward
) -> None:
    """Send a message to the giver to confirm the reward has been given"""
    # CHECK response
    embed = discord.Embed(
        title=':robot: Pouvoir enregistré :moyai:',
        description=f'player : <@{user.id}>\nreward : {reward}',
        color=COLOR_GREEN,
    )
    await interaction.followup.send(embed=embed)


async def message_give_reward_success_to_recipient(
        interaction: discord.Interaction,
        user: discord.Member,
        reward: Reward
) -> None:
    """Send a message to the recipient to confirm the reward has been given"""
    # CHECK response
    embed = discord.Embed(
        title=f':robot: Tu as reçu le pouvoir {reward} :moyai:',
        description="Tu peux dès à présent l'utiliser dans le serveur, à condition qu'il n'y ai pas de vote en cours.",
        color=COLOR_GREEN,
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url,
    )
    embed.add_field(
        name='Comment faire ?',
        value="Il suffit d'utiliser la commande `/pouvoir` dans un channel du serveur, où bien ici en MP avec moi.",
        inline=False
    )
    await user.send(embed=embed)


async def message_you_dont_have_this_power(
        interaction: discord.Interaction,
        power: str
) -> None:
    """Send a message to inform the user that he doesn't have this power"""
    # CHECK response
    embed = discord.Embed(
        title=":robot: Vous n'avez pas ce pouvoir ! :moyai:",
        description=f'pouvoir : {power}',
        color=COLOR_RED,
    )
    await interaction.followup.send(embed=embed)


async def message_not_an_executable_power(
        interaction: discord.Interaction,
        power: str
) -> None:
    """Send a message to inform the user that the power is not executable"""
    # CHECK response
    embed = discord.Embed(
        title=":robot: Ce pouvoir n'est pas executable ! :moyai:",
        description=f'pouvoir : {power}',
        color=COLOR_ORANGE,
    )
    await interaction.followup.send(embed=embed)


async def message_user_not_alive(interaction: discord.Interaction) -> None:
    """Send a message to inform the user that he is not alive"""
    # CHECK response
    embed = discord.Embed(
        title=':robot: Tu as été éliminé ! :moyai:',
        description='En tant que joueur éliminé, tu ne peux pas utiliser de pouvoir.',
        color=COLOR_RED,
    )
    await interaction.followup.send(embed=embed)


async def message_vote_in_progress(
        interaction: discord.Interaction,
        power: str
) -> None:
    """Send a message to inform the user that a vote is in progress"""
    # CHECK response
    embed = discord.Embed(
        title=":robot: Impossible d'utiliser un pouvoir quand un vote est en cours ! :moyai:",
        description=f'pouvoir : {power}',
        color=COLOR_RED,
    )
    await interaction.followup.send(embed=embed)


async def setup(bot):
    """Setup the cog."""

    await bot.add_cog(RewardsCog(bot))
    logger.debug('Loaded !')
