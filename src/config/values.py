from dotenv import load_dotenv  # for python-dotenv method

load_dotenv()
import os

EMOJIS_LIST = [
    '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
    '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿'
]  # Définition de la liste des émojis de réaction pour les votes

# Mode (dev/production)
MODE = os.environ.get('MODE').upper()

# Database URI
MONGODB_URI = os.environ.get('MongoDB_URI')

# Bot Tokens
TOKEN = os.environ.get('TOKEN')
APPLICATION_ID = os.environ.get('APPLICATION_ID')

# Discord channels IDs
CHANNEL_ID_BOT_PRIVATE = int(os.environ.get('CHANNEL_BOT_PRIVATE'))
CHANNEL_ID_BOT = int(os.environ.get('CHANNEL_BOT'))
CHANNEL_ID_BOT_LOGS = int(os.environ.get('CHANNEL_BOT_LOGS'))
CHANNEL_ID_GENERAL = int(os.environ.get('CHANNEL_GENERAL'))
CHANNEL_ID_INSCRIPTION = int(os.environ.get('CHANNEL_INSCRIPTION'))
CHANNEL_ID_VOTE = int(os.environ.get('CHANNEL_VOTE'))
CHANNEL_ID_RESULTATS = int(os.environ.get('CHANNEL_RESULTATS'))
CHANNEL_ID_HELP_ALLIANCE = int(os.environ.get('CHANNEL_HELP_ALLIANCE'))
CHANNEL_ID_RULES = int(os.environ.get('CHANNEL_RULES'))
CHANNEL_ID_ANNONCES = int(os.environ.get('CHANNEL_ANNONCES'))

# Discord categories IDs
CATEGORIE_ID_ALLIANCES = int(os.environ.get('CATEGORIE_ALLIANCES'))

# Discord IDs
GUILD_ID = int(os.environ.get('GUILD_ID'))
USER_ID_ADMIN = int(os.environ.get('USER_ID_ADMIN'))
BOT_ID = int(os.environ.get('BOT_ID'))

# Collar Immunity Settings
EMOJI_ID_COLLIER = int(os.environ.get('EMOJI_ID_COLLIER'))
HIDDEN_VOTE_PROBABILITY = float(os.environ.get('HIDDEN_VOTE_PROBABILITY'))

# Embed Colors
COLOR_GREEN = 0x008000
COLOR_ORANGE = 0xff7f00
COLOR_RED = 0xf00020
