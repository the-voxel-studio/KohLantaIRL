from bson import ObjectId
import typing
from datetime import datetime

try:
    from database.database import db
    from utils.logging import get_logger
except ImportError:
    from ..utils.logging import get_logger
    from .database import db

logger = get_logger(__name__)

RewardCategories = typing.Literal['mute', 'block', 'resurrect', 'doubleVote']
RewardCategoriesList = list(RewardCategories.__args__)


class Reward:
    """Reward class to store reward data."""

    def __init__(
            self,
            player_id: int,
            category: RewardCategories
    ) -> None:
        """Initialize the reward class."""

        self.player_id: int = player_id
        self.category: RewardCategories = category

    def __str__(self) -> str:
        """Get the reward as a string."""

        return f'{self.player_id}, {self.category}'

    def __repr__(self) -> str:
        """Get the reward as a string."""

        return f'{type(self).__name__}(player_id={self.player_id}, category={self.category})'

    def __eq__(self, other):
        """Check if two rewards are equals."""

        if isinstance(other, Reward):
            return self.player_id == other.player_id and self.category == other.category
        return False


class RewardUsed:
    """RewardUsed class to store reward data when used."""

    def __init__(
            self,
            player_id: int,
            category: RewardCategories,
            target_id: int = 0,
            date: datetime | None = None
    ) -> None:
        """Initialize the reward class."""

        self.player_id: int = player_id
        self.target_id: int = target_id
        self.category: RewardCategories = category
        self.date: datetime = date if date else datetime.now()

    def __str__(self) -> str:
        """Get the reward used as a string."""

        return f'{self.player_id}, {self.category}, {self.target_id}, {self.date}'

    def __repr__(self) -> str:
        """Get the reward used as a string."""

        return f'{type(self).__name__}(player_id={self.player_id}, category={self.category}, target_id={self.target_id}, date={self.date})'

    def __eq__(self, other) -> bool:
        """Check if two rewards used are equals."""

        if isinstance(other, RewardUsed):
            return self.player_id == other.player_id and self.category == other.category and self.target_id == other.target_id and self.date == other.date
        return False

    @property
    def seconds_from_date_to_now(self) -> int:
        """Get the seconds from the reward use to now."""

        return (datetime.now() - self.date).total_seconds()

    @property
    def less_than_a_day_ago(self) -> bool:
        """Check if the reward was used less than a day ago."""

        return self.seconds_from_date_to_now < 86400


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
    def immunite_collar_gived(self) -> bool:
        """Get the immunite collar gived state."""

        immunite_collar_gived = bool(db.Game.find_one({}).get('immunite_collar_gived', False))
        logger.info(f'get immunite_collar_gived: {immunite_collar_gived}')
        return immunite_collar_gived

    @immunite_collar_gived.setter
    def immunite_collar_gived(self, value: bool) -> None:
        """Set the immunite collar gived state."""

        logger.info(f'set immunite_collar_gived: {value}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={'$set': {'immunite_collar_gived': value}}
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

    @property
    def rewards(self) -> list[Reward]:
        """Get the rewards."""

        rewards = [
            Reward(
                int(reward.get('id', 0)),
                reward.get('category', '')
            )
            for reward in db.Game.find_one({}).get('rewards', [])
        ]
        logger.info(f'get rewards: {rewards}')
        return rewards

    @rewards.setter
    def rewards(self, rewards: list[Reward]) -> None:
        """Set the rewards."""

        logger.info(f'set rewards: {rewards}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={
                '$set': {
                    'rewards': [
                        {
                            'id': str(reward.player_id),
                            'category': reward.category
                        }
                        for reward in rewards
                    ]
                }
            }
        )

    @property
    def rewards_used(self) -> list[RewardUsed]:
        """Get the rewards already used."""

        rewards_used = []

        for reward_used in db.Game.find_one({}).get('rewards_used', []):
            date = reward_used.get('date', None)
            if type(date) is str:
                date = datetime.fromisoformat(date)
            rewards_used.append(
                RewardUsed(
                    int(reward_used.get('id', 0)),
                    reward_used.get('category', ''),
                    int(reward_used.get('target_id', 0)),
                    date
                )
            )

        logger.info(f'get rewards_used: {rewards_used}')
        return rewards_used

    @rewards_used.setter
    def rewards_used(self, rewards: list[RewardUsed]) -> None:
        """Set the rewards already used."""

        logger.info(f'set rewards_used: {rewards}')
        db.Game.update_one(
            filter={'_id': self.__id},
            update={
                '$set': {
                    'rewards_used': [
                        {
                            'id': str(reward.player_id),
                            'category': reward.category,
                            'target_id': str(reward.target_id),
                            'date': reward.date if reward.date else datetime.now().isoformat()
                        }
                        for reward in rewards
                    ]
                }
            }
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

    def add_reward(self, reward: Reward) -> None:
        """Add a reward."""

        old_value = self.rewards
        if reward.category not in RewardCategoriesList:
            raise ValueError(f'Invalid reward category: {reward.category}')
        self.rewards = old_value + [reward]

    def add_reward_used(self, reward: RewardUsed) -> None:
        """Add a reward already used."""

        old_value = self.rewards_used
        if reward.category not in RewardCategoriesList:
            raise ValueError(f'Invalid reward category: {reward.category}')
        self.rewards_used = old_value + [reward]

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

    def remove_reward(self, reward_to_remove: Reward) -> None:
        """Remove a reward."""

        old_value = self.rewards

        logger.debug(reward_to_remove)
        logger.debug(old_value)
        logger.debug(old_value == reward_to_remove)

        if reward_to_remove in old_value:
            old_value.remove(reward_to_remove)
            self.rewards = old_value
            logger.debug(old_value)
            return True
        return False


Game = GameModel()
