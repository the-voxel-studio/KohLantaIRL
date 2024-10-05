import discord

from config.values import COLOR_GREEN, COLOR_ORANGE

from database.game import Game, Reward, RewardUsed
from database.player import Player

from utils.punishments import timeout
from utils.logging import get_logger

logger = get_logger(__name__)


async def muting_reward(
        interaction: discord.Interaction,
        user: discord.Member,
        player: Player,
        target: discord.Member
) -> None:

    """Mute the target."""

    logger.info(f'Power execution | Requested by {interaction.user} (id:{interaction.user.id}) | power: mute | target : {target.name} (id:{target.id})')

    # CHECK verify if the target is alive
    # Checking if the target is alive
    # If it's not the case, the power can't be used
    if not Player(id=target.id).object.alive:
        logger.warning(f'Power execution : abort : not alive | Requested by {interaction.user} (id:{interaction.user.id}) | power: mute | target : {target.name} (id:{target.id})')
        await message_target_not_alive(interaction, target)
        return

    # CHECK check that the target is not already under the effect of a power
    # Checking if the target have already been on the effect of a power in the last 24 hours
    # If it's the case, the power can't be used
    already_used_rewards = Game.rewards_used
    if any(
            reward.target_id == target.id and reward.less_than_a_day_ago
            for reward in already_used_rewards
    ):
        logger.warning(f'Power execution : abort : target already attacked less thant a day ago | Requested by {interaction.user} (id:{interaction.user.id}) | power: mute | target : {target.name} (id:{target.id})')
        await message_target_already_attacked(interaction, target)
        return

    # CHECK mute the target
    # Muting the target
    await timeout(
        target,
        author=user,
        minutes=1440,
        reason='Muting power'
    )

    # CHECK register the power as used
    # Resgistre the power as used
    Game.add_reward_used(RewardUsed(player.object.id, 'mute', target.id))

    # CHECK remove power to the user
    # Remove the power to the user (in order not to be able to use it again)
    Game.remove_reward(Reward(player.object.id, 'mute'))

    # CHECK inform the target
    await message_succes_to_target(target)

    # CHECK inform the user
    await message_succes_to_user(interaction, target)


async def message_succes_to_target(
        user: discord.Member,
        target: discord.Member
) -> None:
    """Inform the target that he has been muted."""
    # CHECK message
    embed = discord.Embed(
        title=':robot: Vous avez été mute par un joueur ! :moyai:',
        description=f"<@{user.id}> a choisi d'utiliser son pouvoir sur vous !\ndurée : 24h",
        color=COLOR_ORANGE,
    )
    await target.send(embed=embed)


async def message_succes_to_user(
        interaction: discord.Interaction,
        target: discord.Member
) -> None:
    """Inform the user that the power has been used."""
    # CHECK message
    embed = discord.Embed(
        title=':robot: Mute effectué :moyai:',
        description=f'cible : <@{target.id}>\ndurée : 24h',
        color=COLOR_GREEN,
    )
    await interaction.followup.send(embed=embed)


async def message_target_already_attacked(
        interaction: discord.Interaction,
        target: discord.Member
) -> None:
    """Inform the user that the target has already been attacked."""
    # CHECK message
    embed = discord.Embed(
        title=":robot: Cible déjà sous l'effet d'un pouvoir :moyai:",
        description=f'Le joueur sélectionné a été ciblé par un pouvoir il y a moins de 24h, il est donc impossible de le cibler à nouveau.\n\ncible : <@{target.id}>\ndurée : 24h',
        color=COLOR_ORANGE,
    )
    await interaction.followup.send(embed=embed)


async def message_target_not_alive(
        interaction: discord.Interaction,
        target: discord.Member
) -> None:
    """Inform the user that the target is not alive."""
    # CHECK message
    embed = discord.Embed(
        title=':robot: Cible déjà éliminée :moyai:',
        description=f'Le joueur sélectionné a été éliminé, il est donc impossible de le cibler.\n\ncible : <@{target.id}>',
        color=COLOR_ORANGE,
    )
    await interaction.followup.send(embed=embed)
