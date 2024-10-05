import discord

from config.values import COLOR_GREEN, COLOR_ORANGE

from database.game import Game, Reward, RewardUsed
from database.player import Player

from utils.logging import get_logger

logger = get_logger(__name__)


async def blocking_reward(
        interaction: discord.Interaction,
        user: discord.Member,
        player: Player,
        target: discord.Member
) -> None:

    """Reusrect the target."""

    logger.info(f'Power execution | Requested by {interaction.user} (id:{interaction.user.id}) | power: block | target : {target.name} (id:{target.id})')

    # CHECK verify if the target is not alive
    # Checking if the target is not alive
    # If it's not the case, the power can't be used
    if not Player(id=target.id).object.alive:
        logger.warning(f'Power execution : abort : not alive | Requested by {interaction.user} (id:{interaction.user.id}) | power: block | target : {target.name} (id:{target.id})')
        await message_target_not_alive(interaction, target)
        return

    # CHECK that the target is not already under the effect of a power
    # Checking if the target have already been on the effect of a power in the last 24 hours
    # If it's the case, the power can't be used
    already_used_rewards = Game.rewards_used
    if any(
            reward.target_id == target.id and reward.less_than_a_day_ago
            for reward in already_used_rewards
    ):
        logger.warning(f'Power execution : abort : target already attacked less thant a day ago | Requested by {interaction.user} (id:{interaction.user.id}) | power: block | target : {target.name} (id:{target.id})')
        await message_target_already_attacked(interaction, target)
        return

    # CHECK register the power as used
    # Register the power as used
    # It is also the way that the power is used
    # At the end of a vote, it will check which blocking power has been used less than 24h ago
    Game.add_reward_used(RewardUsed(player.object.id, 'block', target.id))

    # CHECK remove power to the user
    # Remove the power to the user (in order not to be able to use it again)
    Game.remove_reward(Reward(player.object.id, 'block'))

    # CHECK inform the target
    await message_succes_to_target(target)

    # CHECK inform the user
    await message_succes_to_user(interaction, target)


async def message_succes_to_target(
        user: discord.Member,
        target: discord.Member
) -> None:
    """Inform the target that he has been blocked."""
    # CHECK message
    embed = discord.Embed(
        title=':robot: Vous avez été empêché de vote par un joueur ! :moyai:',
        description=f"<@{user.id}> a choisi d'utiliser son pouvoir sur vous !\nVous ne pourrez donc pas voter lors du prochain vote.",
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
        title=':robot: Bloquage effectué :moyai:',
        description=f'cible : <@{target.id}>',
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
        title=':robot: Cible éliminée :moyai:',
        description=f'Le joueur sélectionné est éliminé, il est donc impossible de le cibler avec ce pouvoir.\n\ncible : <@{target.id}>',
        color=COLOR_ORANGE,
    )
    await interaction.followup.send(embed=embed)
