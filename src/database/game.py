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

        vote_msg_id = int(db.Game.find_one({}).get('vote_msg_id', 0))
        logger.info(f'get vote_msg_id: {vote_msg_id}')
        return vote_msg_id

    @vote_msg_id.setter
    def vote_msg_id(self, value: int) -> None:
        """Set the vote message id."""

        logger.info(f'set vote_msg_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'vote_msg_id': str(value)}}
        )

    @property
    def btn_how_to_alliance_msg_id(self) -> int:
        """Get the btn_how_to_alliance message id."""

        btn_how_to_alliance_msg_id = int(db.Game.find_one({}).get('btn_how_to_alliance_msg_id', 0))
        logger.info(f'get btn_how_to_alliance_msg_id: {btn_how_to_alliance_msg_id}')
        return btn_how_to_alliance_msg_id

    @btn_how_to_alliance_msg_id.setter
    def btn_how_to_alliance_msg_id(self, value: int) -> None:
        """Set the btn_how_to_alliance message id."""

        logger.info(f'set btn_how_to_alliance_msg_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'btn_how_to_alliance_msg_id': str(value)}}
        )

    @property
    def last_winner_id(self) -> int:
        """Get the last winner id."""

        last_winner_id = int(db.Game.find_one({}).get('last_winner_id', 0))
        logger.info(f'get last_winner_id: {last_winner_id}')
        return last_winner_id

    @last_winner_id.setter
    def last_winner_id(self, value: int) -> None:
        """Set the last winner id."""

        logger.info(f'set last_winner_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'last_winner_id': str(value)}}
        )

    @property
    def immunite_collar_msg_id(self) -> int:
        """Get the immunite collar message id."""

        immunite_collar_msg_id = int(db.Game.find_one({}).get('immunite_collar_msg_id', 0))
        logger.info(f'get immunite_collar_msg_id: {immunite_collar_msg_id}')
        return immunite_collar_msg_id

    @immunite_collar_msg_id.setter
    def immunite_collar_msg_id(self, value: int) -> None:
        """Set the immunite collar message id."""

        logger.info(f'set immunite_collar_msg_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'immunite_collar_msg_id': str(value)}}
        )

    @property
    def collar_imunized_players_id(self) -> list:
        """Get the immunite collar players id."""

        collar_imunized_players_id = [int(id) for id in db.Game.find_one({}).get('collar_imunized_players_id', [])]
        logger.info(f'get collar_imunized_players_id: {collar_imunized_players_id}')
        return collar_imunized_players_id

    @collar_imunized_players_id.setter
    def collar_imunized_players_id(self, value: list) -> None:
        """Set the immunite collar players ids."""

        logger.info(f'set collar_imunized_players_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'collar_imunized_players_id': [str(id) for id in value]}}
        )

    @property
    def ephemerally_imunized_players_id(self) -> list:
        """Get the epphemerally imunised players id."""

        ephemerally_imunized_players_id = [int(id) for id in db.Game.find_one({}).get('ephemerally_imunized_players_id', [])]
        logger.info(f'get ephemerally_imunized_players_id: {ephemerally_imunized_players_id}')
        return ephemerally_imunized_players_id

    @ephemerally_imunized_players_id.setter
    def ephemerally_imunized_players_id(self, value: list) -> None:
        """Set the ephemerally imunised player ids."""

        logger.info(f'set ephemerally_imunized_players_id: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'ephemerally_imunized_players_id': [str(id) for id in value]}}
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

    def add_collar_imunized_player_id(self, player_id: int) -> None:
        """Add a player to the collar imunized players."""

        old_value = self.collar_imunized_players_id
        if player_id not in old_value:
            self.collar_imunized_players_id = old_value + [player_id]

    def add_ephemerally_imunized_player_id(self, player_id: int) -> None:
        """Add a player to the ephemerally imunized players."""

        old_value = self.ephemerally_imunized_players_id
        if player_id not in old_value:
            self.ephemerally_imunized_players_id = old_value + [player_id]

    def remove_collar_imunized_player_id(self, player_id: int) -> bool:
        """ Remove a player to the collar imunized players."""

        old_value = self.collar_imunized_players_id
        if player_id in old_value:
            self.collar_imunized_players_id = [id for id in old_value if id != player_id]
            return True
        else:
            return False

    def remove_ephemerally_imunized_player_id(self, player_id: int) -> bool:
        """ Remove a player to the ephemerally imunized players."""

        old_value = self.ephemerally_imunized_players_id
        if player_id in old_value:
            self.ephemerally_imunized_players_id = [id for id in old_value if id != player_id]
            return True
        else:
            return False


Game = GameModel()
