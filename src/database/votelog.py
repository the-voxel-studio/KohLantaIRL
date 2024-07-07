from datetime import datetime
from random import random

from bson.objectid import ObjectId

try:
    from config.values import HIDDEN_VOTE_PROBABILITY
    from database.alliance import get_alliances_number
    from database.database import db
    from database.player import Player, PlayerList
    from utils.logging import get_logger
except ImportError:
    from ..config.values import HIDDEN_VOTE_PROBABILITY
    from ..database.alliance import get_alliances_number
    from ..database.player import Player, PlayerList
    from ..utils.logging import get_logger
    from .database import db

logger = get_logger(__name__)


class VoteLogData:
    """VoteLog data class to store votelog data."""

    def __init__(self, data: dict = {}) -> None:
        """Initialize the votelog data class with the data."""

        self._id: int = data.get('_id', 0)
        self.number: int = data.get('number', 0)
        self.date: str = data.get('date', '')
        eliminated: list[str, ObjectId] = data.get('eliminated', [])
        votes: list[dict[str, ObjectId]] = data.get('votes', [])
        self.voice_id: int = data.get('voice_id', 0)
        self.voters_number: int = data.get('voters_number', 0)
        self.cheaters_number: int = data.get('cheaters_number', 0)
        tied_players: list[dict[str, ObjectId]] = data.get('tied_players', [])
        self.alliance_number: int = data.get('alliance_number', 0)
        self.hidden: bool = data.get('hidden', random() < HIDDEN_VOTE_PROBABILITY)
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
            self.eliminated = PlayerList([{'_id': player} for player in eliminated])
        else:
            self.eliminated = PlayerList()
        if tied_players:
            self.tied_players = PlayerList([{'_id': player} for player in tied_players])
        else:
            self.tied_players = PlayerList()


class VoteLog:
    """VoteLog class to store votelog object and methods."""

    def __init__(self, data: dict = {}, **query) -> None:
        """Initialize the votelog class with the data and query."""

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

    def __str__(self) -> str:
        """Return the string representation of the votelog object."""

        return f'VoteLog<{(self.object._id, self.object.number)}>'

    def __repr__(self) -> str:
        """Return the string representation of the votelog object."""

        return f'VoteLog<{(self.object._id, self.object.number)}>'

    def find(self) -> None:
        """Find the votelog object from the database."""

        data: dict = db.VoteLog.find_one(filter=self.query)
        if data:
            self.object = VoteLogData(data)
            logger.info(f'found: {self.object.__dict__}')

    def set_from_data(self, data: dict) -> None:
        """Set the votelog object from the data."""

        if data:
            self.object = VoteLogData(data)
            logger.info(f'created from data: {self.object.__dict__}')

    def save(self) -> None:
        """Save the votelog object to the database."""

        if self.object:
            if self.object._id:
                object = {k: v for k, v in self.object.__dict__.items() if k != '_id'}
                logger.info(f'update: {self.object.__dict__}')
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
                self.object.votes = [
                    {'voter': vote['voter'].object._id, 'for': vote['for'].object._id}
                    for vote in self.object.votes
                ]
                self.object.tied_players = [player.object._id for player in self.object.tied_players.objects]
                self.object.eliminated = [player.object._id for player in self.object.eliminated.objects]
                logger.info(f'save: {self.object.__dict__}')
                db.VoteLog.insert_one(self.object.__dict__)

    def delete(self) -> None:
        """Delete the votelog object from the database."""

        db.VoteLog.delete_one({'_id': self.object._id})
        logger.info(f'delete: {self.object.__dict__}')
        self.object = VoteLogData()


class VoteLogList:
    """VoteLog list class to store votelog objects."""

    def __init__(self, data: list = [], **query) -> None:
        """Initialize the votelog list class with the data and query."""

        self.query: dict = query
        self.objects: list[VoteLog] = []
        self.find(data)

    def __str__(self) -> str:
        """Return the string representation of the votelog list."""

        return f'VoteLogList<{[(votelog.object._id, votelog.object.number) for votelog in self.objects]}>'

    def __repr__(self) -> str:
        """Return the string representation of the votelog list."""

        return f'VoteLogList<{[(votelog.object._id, votelog.object.number) for votelog in self.objects]}>'

    def __len__(self) -> int:
        """Return the number of votelogs in the list."""

        return len(self.objects)

    def find(self, data) -> None:
        """Find the votelogs from the database."""

        if data:
            self.data = data
        else:
            self.data = db.VoteLog.find(filter=self.query)
        if self.data:
            logger.info(f"{'VoteLogList found' if not data else 'VoteLogList created from data'}")
            for player in self.data:
                self.objects.append(VoteLog(data=player))


def get_council_number():
    """Return the number of council."""

    return db.VoteLog.count_documents({})
