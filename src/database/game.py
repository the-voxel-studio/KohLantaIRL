from bson import ObjectId

try:
    from database.database import db
    from utils.logging import get_logger
except ImportError:
    from ..utils.logging import get_logger
    from .database import db

logger = get_logger(__name__)


class GameModel:
    """Game model class to store game data."""

    def __init__(self) -> None:
        """Initialize the game model class."""

        self.__id: ObjectId = db.Game.find_one({}).get('_id', 0)
        logger.info(f'setup _id: {self.__id}')

    @property
    def state(self) -> int:
        """Get the state of the game."""

        state = db.Game.find_one({}).get('state', 0)
        logger.info(f'get state: {state}')
        return state

    @state.setter
    def state(self, value: int) -> None:
        """Set the state of the game."""

        logger.info(f'set state: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'state': value}}
        )

    @property
    def vote_msg_id(self) -> int:
        """Get the vote message id."""

        vote_msg_id = db.Game.find_one({}).get('vote_msg_id', 0)
        logger.info(f'get vote_msg_id: {vote_msg_id}')
        return vote_msg_id

    @vote_msg_id.setter
    def vote_msg_id(self, value: int) -> None:
        """Set the vote message id."""

        logger.info(f'set vote_msg_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'vote_msg_id': value}}
        )

    @property
    def btn_how_to_alliance_msg_id(self) -> int:
        """Get the btn_how_to_alliance message id."""

        btn_how_to_alliance_msg_id = db.Game.find_one({}).get('btn_how_to_alliance_msg_id', 0)
        logger.info(f'get btn_how_to_alliance_msg_id: {btn_how_to_alliance_msg_id}')
        return btn_how_to_alliance_msg_id

    @btn_how_to_alliance_msg_id.setter
    def btn_how_to_alliance_msg_id(self, value: int) -> None:
        """Set the btn_how_to_alliance message id."""

        logger.info(f'set btn_how_to_alliance_msg_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'btn_how_to_alliance_msg_id': value}}
        )

    @property
    def last_winner_id(self) -> int:
        """Get the last winner id."""

        last_winner_id = db.Game.find_one({}).get('last_winner_id', 0)
        logger.info(f'get last_winner_id: {last_winner_id}')
        return last_winner_id

    @last_winner_id.setter
    def last_winner_id(self, value: int) -> None:
        """Set the last winner id."""

        logger.info(f'set last_winner_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'last_winner_id': value}}
        )

    @property
    def immunite_collar_msg_id(self) -> int:
        """Get the immunite collar message id."""

        immunite_collar_msg_id = db.Game.find_one({}).get('immunite_collar_msg_id', 0)
        logger.info(f'get immunite_collar_msg_id: {immunite_collar_msg_id}')
        return immunite_collar_msg_id

    @immunite_collar_msg_id.setter
    def immunite_collar_msg_id(self, value: int) -> None:
        """Set the immunite collar message id."""

        logger.info(f'set immunite_collar_msg_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'immunite_collar_msg_id': value}}
        )

    @property
    def immunite_collar_player_id(self) -> int:
        """Get the immunite collar player id."""

        immunite_collar_player_id = db.Game.find_one({}).get('immunite_collar_player_id', 0)
        logger.info(f'get immunite_collar_player_id: {immunite_collar_player_id}')
        return immunite_collar_player_id

    @immunite_collar_player_id.setter
    def immunite_collar_player_id(self, value: int) -> None:
        """Set the immunite collar player id."""

        logger.info(f'set immunite_collar_player_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'immunite_collar_player_id': value}}
        )

    def open_joining(self) -> None:
        """Open the joining of the game."""

        self.state = 0

    def start_game(self) -> None:
        """Start the game."""

        self.state = 1

    def wait_for_last_vote(self) -> None:
        """Wait for the last vote."""

        self.state = 2

    def start_last_vote(self) -> None:
        """Start the last vote."""

        self.state = 3

    def game_end(self) -> None:
        """End the game."""

        self.state = 4


Game = GameModel()
