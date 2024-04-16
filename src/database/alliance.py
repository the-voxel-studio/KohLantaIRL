try:
    from utils.logging import get_logger
    from database.player import Player, PlayerList
except:
    from ..utils.logging import get_logger
    from ..database.player import Player, PlayerList

from .database import db

logger = get_logger(__name__)

class AllianceData:
    def __init__(self, data) -> None:
        self._id: int = data.get('_id', 0)
        self.text_id: int = data.get('text_id', 0)
        self.voice_id: int = data.get('voice_id', 0)
        self.name: str = data.get('name', '')
        self.members: PlayerList = data.get('members', [])

class Alliance:
    def __init__(self, data: dict = {}, **query) -> None:
        self.query: dict = query
        self.object: AllianceData = None
        if data:
            self.set_from_data(data)
        else:
            self.find()

    def find(self) -> None:
        data: dict = db.Alliances.find_one(filter=self.query)
        if data:
            self.object = AllianceData(data)
            logger.info(f'Alliance found: {self.object.__dict__}')

    def set_from_data(self, data: dict) -> None:
        if data:
            self.object = AllianceData(data)

    def save(self) -> None:
        if self.object:
            db.Alliances.update_one(filter=self.query, update={'$set': self.object.__dict__})

class AllianceList:
    def __init__(self, **query) -> None:
        self.query: dict = query
        self.objects: list[Alliance] = []
        self.find()

    def find(self) -> None:
        self.data = db.Alliances.find(filter=self.query)
        if self.data:
            logger.info(f'AlliancesList found')
            for alliance in self.data:
                self.objects.append(Alliance(data=alliance))