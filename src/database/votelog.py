from datetime import datetime

from bson.objectid import ObjectId

try:
    from database.alliance import get_alliances_number
    from database.database import db
    from database.player import Player
    from utils.logging import get_logger
except ImportError:
    from ..database.alliance import get_alliances_number
    from ..database.player import Player, PlayerList
    from ..utils.logging import get_logger
    from .database import db

logger = get_logger(__name__)


class VoteLogData:
    def __init__(self, data: dict = {}) -> None:
        self._id: int = data.get('_id', 0)
        self.number: int = data.get('number', 0)
        self.date: str = data.get('date', '')
        eliminated: list[dict[str, ObjectId]] = data.get('eliminated', [])
        votes: list[dict[str, ObjectId]] = data.get('votes', [])
        self.voice_id: int = data.get('voice_id', 0)
        self.voters_number: int = data.get('voters_number', 0)
        self.cheaters_number: int = data.get('cheaters_number', 0)
        tied_players: list[dict[str, ObjectId]] = data.get('tied_players', [])
        self.alliance_number: int = data.get('alliance_number', 0)
        if votes:
            players: dict[ObjectId, Player] = {}
            for vote in votes:
                if not players.get(vote['voter']):
                    players[vote['voter']] = Player(_id=vote['voter'])
                if not players.get(vote['for']):
                    players[vote['for']] = Player(_id=vote['for'])
                self.votes: list[dict[str, Player]] = [
                    {
                        'voter': players.get(vote['voter']),
                        'for': players.get(vote['for'])
                    }
                ]
        else:
            self.votes: list[dict[str, Player]] = []
        if eliminated:
            self.eliminated = PlayerList([{'_id': player.get('_id')} for player in eliminated])
        else:
            self.eliminated = PlayerList()
        if tied_players:
            self.tied_players = PlayerList([{'_id': player} for player in tied_players])
        else:
            self.tied_players = PlayerList()


class VoteLog:
    def __init__(self, data: dict = {}, **query) -> None:
        self.query: dict = query
        self.object: VoteLogData = None
        last = self.query.get('last', None)
        # On peut chercher un VoteLog par attribut last
        # last = 3 -> on cherche le 3e dernier VoteLog
        # last = True -> on cherche le dernier VoteLog (équivalent à last = 0)
        if last:
            if last is True:
                last = 0
            self.query = {'number': get_council_number() + last}
        if data:
            self.set_from_data(data)
        else:
            self.find()

    def find(self) -> None:
        data: dict = db.VoteLog.find_one(filter=self.query)
        if data:
            self.object = VoteLogData(data)
            logger.info(f'found: {self.object.__dict__}')

    def set_from_data(self, data: dict) -> None:
        if data:
            self.object = VoteLogData(data)
            logger.info(f'created from data: {self.object.__dict__}')

    def save(self) -> None:
        if self.object:
            if self.object._id:
                object = {k: v for k, v in self.object.__dict__.items() if k != '_id'}
                db.VoteLog.update_one(
                    filter={'_id': self.object._id},
                    update={'$set': object}
                )
            else:
                self.object._id = ObjectId()
                self.object.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self.object.number = get_council_number() + 1
                self.object.voters_number = len(PlayerList(alive=True).objects)
                self.object.alliance_number = get_alliances_number()
                db.VoteLog.insert_one(self.object.__dict__)

    def delete(self) -> None:
        db.VoteLog.delete_one({'_id': self.object._id})
        self.object = VoteLogData()


class VoteLogList:
    def __init__(self, data: list = [], **query) -> None:
        self.query: dict = query
        self.objects: list[VoteLog] = []
        self.find(data)

    def find(self, data) -> None:
        if data:
            self.data = data
        else:
            self.data = db.VoteLog.find(filter=self.query)
        if self.data:
            logger.info(f"{'VoteLogList found' if not data else 'VoteLogList created from data'}")
            for player in self.data:
                self.objects.append(VoteLog(data=player))


def get_council_number():
    return db.VoteLog.count_documents({})
