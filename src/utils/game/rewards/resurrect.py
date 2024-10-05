import discord

from config.values import COLOR_GREEN, COLOR_ORANGE, CHANNEL_ID_RESULTATS

from database.game import Game, Reward, RewardUsed
from database.player import Player

from utils.game.votes.votes import resurrect
from utils.logging import get_logger

logger = get_logger(__name__)


async def resurrecting_reward(
        interaction: discord.Interaction,
        user: discord.Member,
        player: Player,
        target: discord.Member
) -> None:

    """Reusrect the target."""

    logger.info(f'Power execution | Requested by {interaction.user} (id:{interaction.user.id}) | power: resurrect | target : {target.name} (id:{target.id})')

    # CHECK verify if the target is alive
    # Checking if the target is alive
    # If it's not the case, the power can't be used
    if Player(id=target.id).object.alive:
        logger.warning(f'Power execution : abort : alive | Requested by {interaction.user} (id:{interaction.user.id}) | power: resurrect | target : {target.name} (id:{target.id})')
        await message_target_alive(interaction, target)
        return

    # CHECK check that the target is not already under the effect of a power
    # Checking if the target have already been on the effect of a power in the last 24 hours
    # If it's the case, the power can't be used
    already_used_rewards = Game.rewards_used
    if any(
            reward.target_id == target.id and reward.less_than_a_day_ago
            for reward in already_used_rewards
    ):
        logger.warning(f'Power execution : abort : target already attacked less thant a day ago | Requested by {interaction.user} (id:{interaction.user.id}) | power: resurect | target : {target.name} (id:{target.id})')
        await message_target_already_attacked(interaction, target)
        return

    # CHECK resurect the target
    # Resurect the target
    await resurrect(
        interaction,
        target,
        player,
        dm_message=False,
        interaction_response=False
    )

    # CHECK register the power as used
    # Resgistre the power as used
    Game.add_reward_used(RewardUsed(player.object.id, 'resurrect', target.id))

    # CHECK remove power to the user
    # Remove the power to the user (in order not to be able to use it again)
    Game.remove_reward(Reward(player.object.id, 'resurrect'))

    # CHECK inform the target
    await message_succes_to_target(target, user)

    # CHECK inform the user
    await message_succes_to_user(interaction, target)

    # CHECK inform the server
    await message_succes_to_server(interaction, target)


async def message_succes_to_target(
        user: discord.Member,
        target: discord.Member
) -> None:
    """Inform the target that he has been resurrected."""
    # CHECK message
    embed = discord.Embed(
        title=':robot: Vous avez été réintégré par un joueur ! :moyai:',
        description=f"<@{user.id}> a choisi d'utiliser son pouvoir sur vous !",
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
        title=':robot: Résurection effectuée :moyai:',
        description=f'cible : <@{target.id}>',
        color=COLOR_GREEN,
    )
    await interaction.followup.send(embed=embed)


async def message_succes_to_server(
        interaction: discord.Interaction,
        target: discord.Member
) -> None:
    """Inform the sever members that the power has been used."""
    # CHECK message
    embed = discord.Embed(
        title=f"J'ai décidé de réintégrer {target.display_name} !",
        description=f"Suite à l'usage de son pouvoir, <@{interaction.user.id}> a décidé de réintégrer <@{target.id}> dans le jeu.",
        color=COLOR_GREEN,
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url,
    )
    results_channel = interaction.guild.get_channel(CHANNEL_ID_RESULTATS)
    await results_channel.send(embed=embed)


async def message_target_alive(
        interaction: discord.Interaction,
        target: discord.Member
) -> None:
    """Inform the user that the target is alive."""
    # CHECK message
    embed = discord.Embed(
        title=':robot: Cible non éliminée :moyai:',
        description=f'Le joueur sélectionné est encore en jeu, il est donc impossible de le cibler avec ce pouvoir.\n\ncible : <@{target.id}>',
        color=COLOR_ORANGE,
    )
    await interaction.followup.send(embed=embed)
