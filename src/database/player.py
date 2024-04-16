try:
    from utils.logging import get_logger
except:
    from ..utils.logging import get_logger

from .database import db

logger = get_logger(__name__)

class PlayerData:
    def __init__(self, data) -> None:
        self._id: int = data.get('_id', 0)
        self.id: int = data.get('id', 0)
        self.nickname: str = data.get('nickname', '')
        self.alive: bool = data.get('alive', False)
        self.letter: str = data.get('letter', '')
        self.last_wish_expressed: bool = data.get('lastWishExpressed', False)
        self.death_council_number: int = data.get('deathCouncilNumber', 0)

class Player:
    def __init__(self, data: dict = {}, **query) -> None:
        self.query: dict = query
        self.object: PlayerData = None
        if data:
            self.set_from_data(data)
        else:
            self.find()

    def find(self) -> None:
        data: dict = db.Players.find_one(filter=self.query)
        if data:
            self.object = PlayerData(data)
            logger.info(f'Player found: {self.object.__dict__}')

    def set_from_data(self, data: dict) -> None:
        if data:
            self.object = PlayerData(data)

    def save(self) -> None:
        if self.object:
            db.Players.update_one(filter=self.query, update={'$set': self.object.__dict__})

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
    def __init__(self, **query) -> None:
        self.query: dict = query
        self.objects: list[Player] = []
        self.find()

    def find(self) -> None:
        self.data = db.Players.find(filter=self.query)
        if self.data:
            logger.info(f'PlayerList found')
            for player in self.data:
                self.objects.append(Player(data=player))