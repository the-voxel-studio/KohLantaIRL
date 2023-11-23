import discord
from config.values import APPLICATION_ID

INTENTS = (intents) = discord.Intents.all()  # Importation des capacités de controle du robot
intents.guilds = True
bot = discord.ext.commands.Bot(
    command_prefix="/",
    description=f"Bot maitre du jeu",
    intents=INTENTS,
    # application_id=APPLICATION_ID,
    help_command=None
)
client = discord.Client(intents=INTENTS)
# client = discord.Client(intents=INTENTS,application_id=APPLICATION_ID)