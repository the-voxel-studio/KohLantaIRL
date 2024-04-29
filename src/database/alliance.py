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
    """Alliance data class to store alliance data."""

    def __init__(self, data: dict = {}) -> None:
        """Initialize the alliance data class with the data."""

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
    """Alliance class to store alliance object and methods."""

    def __init__(self, data: dict = {}, **query) -> None:
        """Initialize the alliance class with the data and query."""

        self.query: dict = query
        self.object: AllianceData = None
        if data:
            self.query = data
            self.set_from_data()
        else:
            self.find()

    def __str__(self) -> str:
        """Return the string representation of the alliance object."""

        return f'Alliance<{(self.object._id, self.object.name)}>'

    def __repr__(self) -> str:
        """Return the string representation of the alliance object."""

        return f'Alliance<{(self.object._id, self.object.name)}>'

    def find(self) -> None:
        """Find the alliance object from the database."""

        data: dict = db.Alliances.find_one(filter=self.query)
        if data:
            self.object = AllianceData(data)
            logger.info(f'found: {self.object.__dict__}')

    def set_from_data(self) -> None:
        """Set the alliance object from the data."""

        self.object = AllianceData(self.query)
        logger.info(f'created from data: {self.object.__dict__}')

    def save(self) -> None:
        """Save the alliance object to the database."""

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
        """Delete the alliance object from the database."""

        db.Alliances.delete_one({'_id': self.object._id})
        logger.info(f'delete: {self.object.__dict__}')
        self.object = AllianceData()

    def close(self) -> None:
        """Close the alliance."""

        db.Alliances.update_one(filter=self.query, update={'$set': {'members': []}}, upsert=False)
        logger.info(f'close: {self.object.__dict__}')
        self.object.members = []

    def add_member(self, player: Player) -> None:
        """Add a member to the alliance."""

        if player.object._id not in [member.object._id for member in self.object.members.objects]:
            self.object.members.objects.append(player)
            self.save()
            logger.info(f'add_member: {self.object.__dict__}')

    def remove_member(self, player: Player) -> None:
        """Remove a member from the alliance."""

        self.object.members.objects = [member for member in self.object.members.objects if member.object._id != player.object._id]
        self.save()
        logger.info(f'remove_member: {self.object.__dict__}')

    def purge_empty_alliances(self) -> int:
        """Purge empty alliances."""

        self.result = db.Alliances.delete_many({'members': []})
        logger.info('purge_empty_alliances')
        return self.result.deleted_count


class AllianceList:
    """Alliance list class to store alliance list object and methods."""

    def __init__(self, data: list = [], **query) -> None:
        """Initialize the alliance list class with the data and query."""

        self.query: dict = query
        self.objects: list[Alliance] = []
        self.find(data)

    def __str__(self) -> str:
        """Return the string representation of the alliance list object."""

        return f'AllianceList<{[(alliance.object._id, alliance.object.name) for alliance in self.objects]}>'

    def __repr__(self) -> str:
        """Return the string representation of the alliance list object."""

        return f'AllianceList<{[(alliance.object._id, alliance.object.name) for alliance in self.objects]}>'

    def __len__(self) -> int:
        """Return the length of the alliance list object."""

        return len(self.objects)

    def find(self, data) -> None:
        """Find the alliance objects from the database."""

        if data:
            self.data = data
        else:
            self.data = db.Alliances.find(filter=self.query)
        if self.data:
            logger.info(f"{'AllianceList found' if not data else 'AlliancesList created from data'}")
            for player in self.data:
                self.objects.append(Alliance(data=player))


def get_alliances_number():
    """Get the number of alliances."""

    return db.Alliances.count_documents({})
