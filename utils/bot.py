import discord

INTENTS = (
    intents
) = discord.Intents.all()  # Importation des capacités de controle du robot
intents.guilds = True
bot = discord.ext.commands.Bot(
    command_prefix='/',
    description='Bot maitre du jeu',
    intents=INTENTS,
    help_command=None,
)
client = discord.Client(intents=INTENTS)
