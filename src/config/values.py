from dotenv import load_dotenv  # for python-dotenv method

load_dotenv()
import os

MODE = 'dev'
# MODE = 'production'
EMOJIS_LIST = [
    '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
    '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿'
]  # Définition de la liste des émojis de réaction pour les votes
MONGODB_URI = os.environ.get('MongoDB_URI')
CHANNEL_ID_BOT_PRIVATE = int(os.environ.get('CHANNEL_BOT_PRIVATE'))
CHANNEL_ID_BOT = int(os.environ.get('CHANNEL_BOT'))
CHANNEL_ID_BOT_LOGS = int(os.environ.get('CHANNEL_BOT_LOGS'))
CHANNEL_ID_GENERAL = int(os.environ.get('CHANNEL_GENERAL'))
CHANNEL_ID_INSCRIPTION = int(os.environ.get('CHANNEL_INSCRIPTION'))
CHANNEL_ID_VOTE = int(os.environ.get('CHANNEL_VOTE'))
CHANNEL_ID_RESULTATS = int(os.environ.get('CHANNEL_RESULTATS'))
CHANNEL_ID_HELP_ALLIANCE = int(os.environ.get('CHANNEL_ID_HELP_ALLIANCE'))
CHANNEL_ID_ANNONCES = int(os.environ.get('CHANNEL_ID_ANNONCES'))
CHANNEL_RULES = int(os.environ.get('CHANNEL_RULES'))
CATEGORIE_ID_ALLIANCES = int(os.environ.get('CATEGORIE_ALLIANCES'))
EMOJI_ID_COLLIER = int(os.environ.get('EMOJI_ID_COLLIER'))
USER_ID_ADMIN = int(os.environ.get('USER_ID_ADMIN'))
BOT_ID = int(os.environ.get('BOT_ID'))
GUILD_ID = int(os.environ.get('GUILD_ID'))
TOKEN = os.environ.get('TOKEN')
APPLICATION_ID = os.environ.get('APPLICATION_ID')
HIDDEN_VOTE_PROBABILITY = float(os.environ.get('HIDDEN_VOTE_PROBABILITY'))
COLOR_GREEN = 0x008000
COLOR_ORANGE = 0xff7f00
COLOR_RED = 0xf00020
