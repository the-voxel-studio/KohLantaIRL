try:
    from database.database import db
    from utils.logging import get_logger
except ImportError:
    from ..utils.logging import get_logger
    from .database import db

from bson import ObjectId

logger = get_logger(__name__)


class PlayerData:
    """Player data class to store player data."""

    def __init__(self, data: dict = {}) -> None:
        """Initialize the player data class with the data."""

        self._id: int = data.get('_id', 0)
        self.id: int = int(data.get('id', 0))  # To transform into int if it's a big int
        self.nickname: str = data.get('nickname', '')
        self.alive: bool = data.get('alive', False)
        self.letter: str = data.get('letter', '')
        self.last_wish_expressed: bool = data.get('last_wish_expressed', False)
        self.death_council_number: int = data.get('death_council_number', 0)


class Player:
    """Player class to store player object and methods."""

    def __init__(self, data: dict = {}, **query) -> None:
        """Initialize the player class with the data and query."""

        self.query: dict = query
        self.object: PlayerData = PlayerData()
        if isinstance(self.query.get('id', None), int):
            self.query['id'] = str(self.query['id'])
        if data:
            self.set_from_data(data)
        else:
            self.find()

    def __str__(self) -> str:
        """Return the string representation of the player object."""

        return f'Player<{(self.object._id, self.object.nickname)}>'

    def __repr__(self) -> str:
        """Return the string representation of the player object."""

        return f'Player<{(self.object._id, self.object.nickname)}>'

    def find(self) -> None:
        """Find the player object from the database."""

        data: dict = db.Players.find_one(filter=self.query)
        if data:
            self.object = PlayerData(data)
            logger.info(f'found: {self.object.__dict__}')

    def set_from_data(self, data: dict) -> None:
        """Set the player object from the data."""

        if data:
            self.object = PlayerData(data)
            logger.info(f'created from data: {self.object.__dict__}')

    def save(self) -> None:
        """Save the player object to the database."""

        if self.object:
            if self.object._id:
                object = {k: v for k, v in self.object.__dict__.items() if k != '_id'}
                object['id'] = str(object['id'])
                logger.info(f'update: {self.object.__dict__}')
                db.Players.update_one(
                    filter={'_id': self.object._id},
                    update={'$set': object}
                )
            else:
                self.object._id = ObjectId()
                object = self.object.__dict__
                object['id'] = str(object['id'])
                logger.info(f'save: {self.object.__dict__}')
                db.Players.insert_one(object)

    def resurrect(self) -> None:
        """Resurrect the player."""

        if self.object:
            self.object.alive = True
            self.object.letter = ''
            self.death_council_number = 0
            self.object.last_wish_expressed = False
            self.save()
            logger.info(f'resurrect: {self.object.__dict__}')

    def eliminate(self) -> None:
        """Eliminate the player."""

        if self.object:
            self.object.alive = False
            self.object.letter = ''
            self.death_council_number = db.VoteLog.count_documents({})
            logger.info(f'eliminate: {self.object.__dict__}')
            self.save()


class PlayerList:
    """Player list class to store player objects."""

    def __init__(self, data: list[dict] = [], **query) -> None:
        """Initialize the player list class with the data and query."""

        self.query: dict = query
        self.objects: list[Player] = []
        self.find(data)

    def __str__(self) -> str:
        """Return the string representation of the player list object."""

        return f'PlayerList<{[(player.object._id, player.object.nickname) for player in self.objects]}>'

    def __repr__(self) -> str:
        """Return the string representation of the player list object."""

        return f'PlayerList<{[(player.object._id, player.object.nickname) for player in self.objects]}>'

    def __len__(self) -> int:
        """Return the length of the player list object."""

        return len(self.objects)

    def find(self, data) -> None:
        """Find the player objects from the database."""

        if data:
            self.data = data
        else:
            self.data = db.Players.find(filter=self.query)
        if self.data:
            logger.info(f"{'PlayerList found' if not data else 'PlayersList created from data'}")
            for player in self.data:
                self.objects.append(Player(**player))
