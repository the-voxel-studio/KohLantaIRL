try:
    from database.database import db
    from database.player import Player, PlayerData, PlayerList
    from utils.logging import get_logger
except ImportError:
    from ..utils.logging import get_logger
    from ..database.player import Player, PlayerList, PlayerData
    from .database import db

from bson import ObjectId

logger = get_logger(__name__)


class AllianceData:
    def __init__(self, data: dict = {}) -> None:
        self._id: int = data.get('_id', 0)
        self.text_id: int = data.get('text_id', 0)
        self.voice_id: int = data.get('voice_id', 0)
        self.name: str = data.get('name', '')
        members = data.get('members', [])
        if members:
            data: list[PlayerData] = [Player(_id=member).object.__dict__ for member in members]
            self.members: PlayerList = PlayerList(data=data)
        else:
            self.members: PlayerList = None


class Alliance:
    def __init__(self, data: dict = {}, **query) -> None:
        self.query: dict = query
        self.object: AllianceData = None
        if data:
            self.query = data
            self.set_from_data()
        else:
            self.find()

    def find(self) -> None:
        data: dict = db.Alliances.find_one(filter=self.query)
        if data:
            self.object = AllianceData(data)
            logger.info(f'found: {self.object.__dict__}')

    def set_from_data(self) -> None:
        self.object = AllianceData(self.query)
        logger.info(f'created from data: {self.object.__dict__}')

    def save(self) -> None:
        if self.object:
            if self.object._id:
                object = {k: v for k, v in self.object.__dict__.items() if k != '_id'}
                logger.info(f'update: {self.object.__dict__}')
                db.Players.update_one(
                    filter={'_id': self.object._id},
                    update={'$set': object}
                )
            else:
                self.object._id = ObjectId()
                logger.info(f'save: {self.object.__dict__}')
                db.Players.insert_one(self.object.__dict__)

    def delete(self) -> None:
        db.Alliances.delete_one({'_id': self.object._id})
        logger.info(f'delete: {self.object.__dict__}')
        self.object = AllianceData()

    def close(self) -> None:
        db.Alliances.update_one(filter=self.query, update={'$set': {'members': []}}, upsert=False)
        logger.info(f'close: {self.object.__dict__}')
        self.object.members = []

    def add_member(self, player: Player) -> None:
        if player.object._id not in [member.object._id for member in self.object.members.objects]:
            self.object.members.objects.append(player)
            self.save()
            logger.info(f'add_member: {self.object.__dict__}')

    def remove_member(self, player: Player) -> None:
        self.object.members.objects = [member for member in self.object.members.objects if member.object._id != player.object._id]
        self.save()
        logger.info(f'remove_member: {self.object.__dict__}')

    def purge_empty_alliances(self):
        self.result = db.Alliances.delete_many({'members': []})
        logger.info('purge_empty_alliances')


class AllianceList:
    def __init__(self, data: list = [], **query) -> None:
        self.query: dict = query
        self.objects: list[Alliance] = []
        self.find(data)

    def find(self, data) -> None:
        if data:
            self.data = data
        else:
            self.data = db.Alliances.find(filter=self.query)
        if self.data:
            logger.info(f"{'AllianceList found' if not data else 'AlliancesList created from data'}")
            for player in self.data:
                self.objects.append(Alliance(data=player))


def get_alliances_number():
    return db.Alliances.count_documents({})
