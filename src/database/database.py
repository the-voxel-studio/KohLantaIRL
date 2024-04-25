import dns.resolver
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

try:
    from config.values import MONGODB_URI
    from utils.logging import get_logger
except ImportError:
    from ..config.values import MONGODB_URI
    from ..utils.logging import get_logger


logger = get_logger(__name__)
client: MongoClient = None
db: Database = None


def setup_db_connection():
    global client, db
    logger.info('Connection to MongoDb...')
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8']

    client = MongoClient(MONGODB_URI)
    db = client.Game

    try:
        client.admin.command('ping')
        logger.info('Connected to MongoDb')
    except Exception as e:
        logger.error('Connection to MongoDb FAILED')
        logger.error(e)


setup_db_connection()
