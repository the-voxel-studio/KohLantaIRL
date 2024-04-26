from bson import ObjectId

try:
    from database.database import db
    from utils.logging import get_logger
except ImportError:
    from ..utils.logging import get_logger
    from .database import db

logger = get_logger(__name__)


class GameModel:
    def __init__(self) -> None:
        self.__id: ObjectId = db.Game.find_one({}).get('_id', 0)

    @property
    def state(self) -> int:
        return db.Game.find_one({}).get('state', 0)

    @state.setter
    def state(self, value: int) -> None:
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'state': value}}
        )

    @property
    def vote_msg_id(self) -> int:
        return db.Game.find_one({}).get('vote_msg_id', 0)

    @vote_msg_id.setter
    def vote_msg_id(self, value: int) -> None:
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'vote_msg_id': value}}
        )

    @property
    def btn_how_to_alliance_msg_id(self) -> int:
        return db.Game.find_one({}).get('btn_how_to_alliance_msg_id', 0)

    @btn_how_to_alliance_msg_id.setter
    def btn_how_to_alliance_msg_id(self, value: int) -> None:
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'btn_how_to_alliance_msg_id': value}}
        )

    @property
    def last_winner_id(self) -> int:
        return db.Game.find_one({}).get('last_winner_id', 0)

    @last_winner_id.setter
    def last_winner_id(self, value: int) -> None:
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'last_winner_id': value}}
        )

    @property
    def immunite_collar_msg_id(self) -> int:
        return db.Game.find_one({}).get('immunite_collar_msg_id', 0)

    @immunite_collar_msg_id.setter
    def immunite_collar_msg_id(self, value: int) -> None:
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'immunite_collar_msg_id': value}}
        )

    @property
    def immunite_collar_player_id(self) -> int:
        return db.Game.find_one({}).get('immunite_collar_player_id', 0)

    @immunite_collar_player_id.setter
    def immunite_collar_player_id(self, value: int) -> None:
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'immunite_collar_player_id': value}}
        )

    def open_joining(self) -> None:
        self.state = 0

    def start_game(self) -> None:
        self.state = 1

    def wait_for_last_vote(self) -> None:
        self.state = 2

    def start_last_vote(self) -> None:
        self.state = 3

    def game_end(self) -> None:
        self.state = 4


Game = GameModel()
