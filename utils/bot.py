import discord

INTENTS = (intents) = discord.Intents.all()  # Importation des capacités de controle du robot
bot = discord.ext.commands.Bot(
    command_prefix="/",
    description=f"Bot maitre du jeu",
    intents=INTENTS,
    application_id=1139673903678095400,
    help_command=None
)