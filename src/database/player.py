try:
    from database.database import db
    from utils.logging import get_logger
except ImportError:
    from ..utils.logging import get_logger
    from .database import db

from bson import ObjectId

logger = get_logger(__name__)


class PlayerData:
    def __init__(self, data: dict = {}) -> None:
        self._id: int = data.get('_id', 0)
        self.id: int = int(data.get('id', 0))  # To transform into int if it's a big int
        self.nickname: str = data.get('nickname', '')
        self.alive: bool = data.get('alive', False)
        self.letter: str = data.get('letter', '')
        self.last_wish_expressed: bool = data.get('last_wish_expressed', False)
        self.death_council_number: int = data.get('death_council_number', 0)


class Player:
    def __init__(self, data: dict = {}, **query) -> None:
        self.query: dict = query
        self.object: PlayerData = None
        if isinstance(self.query.get('id', None), int):
            self.query['id'] = str(self.query['id'])
        if data:
            self.set_from_data(data)
        else:
            self.find()

    def find(self) -> None:
        data: dict = db.Players.find_one(filter=self.query)
        if data:
            self.object = PlayerData(data)
            logger.info(f'found: {self.object.__dict__}')

    def set_from_data(self, data: dict) -> None:
        if data:
            self.object = PlayerData(data)
            logger.info(f'created from data: {self.object.__dict__}')

    def save(self) -> None:
        if self.object:
            if self.object._id:
                object = {k: v for k, v in self.object.__dict__.items() if k != '_id'}
                object['id'] = str(object['id'])
                db.Players.update_one(
                    filter={'_id': self.object._id},
                    update={'$set': object}
                )
            else:
                self.object._id = ObjectId()
                object = self.object.__dict__
                object['id'] = str(object['id'])
                db.Players.insert_one(object)

    def resurrect(self) -> None:
        if self.object:
            self.object.alive = True
            self.object.letter = ''
            self.death_council_number = 0
            self.object.last_wish_expressed = False
            self.save()

    def eliminate(self) -> None:
        if self.object:
            self.object.alive = False
            self.object.letter = ''
            self.death_council_number = db.VoteLog.count_documents({})
            self.save()


class PlayerList:
    def __init__(self, data: list[dict] = [], **query) -> None:
        self.query: dict = query
        self.objects: list[Player] = []
        self.find(data)

    def find(self, data) -> None:
        if data:
            self.data = data
        else:
            self.data = db.Players.find(filter=self.query)
        if self.data:
            logger.info(f"{'PlayerList found' if data else 'PlayersList created from data'}")
            for player in self.data:
                self.objects.append(Player(**player))
