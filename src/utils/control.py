import discord


def is_admin(user: discord.Member) -> bool:
    """Check if the user is an admin."""

    admin_role = discord.utils.get(user.guild.roles, name='Admin')
    if admin_role in user.roles:
        return True
    return False


def is_in_guild(interaction: discord.Interaction) -> bool:
    """Check if the interaction is in a guild."""

    if interaction.guild:
        return True
    return False
