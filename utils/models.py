from datetime import datetime

import discord
import dns.resolver
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient

from config.values import EMOJIS_LIST, MONGODB_URI
from utils.logging import get_logger

logger = get_logger(__name__)
client = None
db = None


def setup_db_connection():
    global client, db
    logger.info('Connection to MongoDb...')
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8']

    client = MongoClient(MONGODB_URI)
    db = client.Game

    try:
        client.admin.command('ping')
        logger.info('Connected to MongoDb')
    except Exception as e:
        logger.error('Connection to MongoDb FAILED')
        logger.error(e)


class NewPlayer:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0)
        self.nickname = kwargs.get('nickname', 'unknown')
        self.alive = kwargs.get('alive', True)
        self.letter = kwargs.get('letter', '')
        self.death_council_number = kwargs.get('dcn', 0)

    def save(self) -> None:
        db.Players.insert_one(
            {
                'id': self.id,
                'nickname': self.nickname,
                'alive': self.alive,
                'deathCouncilNumber': self.death_council_number,
                'letter': self.letter,
                'lastWishExpressed': False,
                'lastGeneralMessageDate': '',
            }
        )
        logger.info(
            f'fn > NewPlayer saving > OK | Discord id: {self.id} | Nickname: {self.nickname}'
        )


class Player:

    def __init__(self, **kwargs):
        logger.info(f'PlayerObjectCreation | args: {kwargs}')
        self.id = kwargs.get('id', 0)
        self.nickname = kwargs.get('nickname', 'unknown')
        self.alive = kwargs.get('alive', True)
        self.death_council_number = kwargs.get('dcn', 0)
        self.option = kwargs.get('option', 'unknown')
        self.letter = kwargs.get('letter', '')
        self._id = kwargs.get('_id', 0)
        self.exists = False
        self.list = []
        self.player = None
        self.last_wish_expressed = None

        self.find()

    def find(self):
        if self.id != 0:
            self.player = db.Players.find_one(filter={'id': self.id})
            if self.player is not None:
                self.nickname = self.player.get('nickname', 'unknown')
                self.alive = self.player.get('alive', True)
                self.death_council_number = self.player.get('deathCouncilNumber', 0)
                self.letter = self.player.get('letter', '')
                self._id = self.player.get('_id', None)
                self.last_wish_expressed = self.player.get('lastWishExpressed', True)
                self.last_general_message_date = self.player.get(
                    'lastGeneralMessageDate', ''
                )
                self.exists = True
        elif self._id != 0:
            self.player = db.Players.find_one(filter={'_id': self._id})
            if self.player is not None:
                self.nickname = self.player.get('nickname', 'unknown')
                self.alive = self.player.get('alive', True)
                self.death_council_number = self.player.get('deathCouncilNumber', 0)
                self.letter = self.player.get('letter', '')
                self.id = self.player.get('id', None)
                self.last_wish_expressed = self.player.get('lastWishExpressed', True)
                self.last_general_message_date = self.player.get(
                    'lastGeneralMessageDate', ''
                )
                self.exists = True
        elif self.nickname != 'unknown':
            self.player = db.Players.find_one(filter={'nickname': self.nickname})
            if self.player is not None:
                self.id = self.player.get('id', 0)
                self.alive = self.player.get('alive', True)
                self.death_council_number = self.player.get('deathCouncilNumber', 0)
                self.letter = self.player.get('letter', '')
                self._id = self.player.get('_id', None)
                self.last_wish_expressed = self.player.get('lastWishExpressed', True)
                self.last_general_message_date = self.player.get(
                    'lastGeneralMessageDate', ''
                )
                self.exists = True
        elif self.letter != '':
            self.player = db.Players.find_one(filter={'letter': self.letter})
            if self.player is not None:
                self.id = self.player.get('id', 0)
                self.nickname = self.player.get('nickname', 'unknown')
                self.alive = self.player.get('alive', True)
                self.death_council_number = self.player.get('deathCouncilNumber', 0)
                self._id = self.player.get('_id', None)
                self.last_wish_expressed = self.player.get('lastWishExpressed', True)
                self.last_general_message_date = self.player.get(
                    'lastGeneralMessageDate', ''
                )
                self.exists = True
        elif self.option == 'living':
            self.list = list(db.Players.find({'alive': True}))
        elif self.option == 'eliminated':
            self.list = list(db.Players.find({'alive': False}))
        logger.info(
            f'fn > Player find > OK | player: {self.player} | id: {self.id} | _id: {self._id} | nickname: {self.nickname} | alive: {self.alive} | dCN: {self.death_council_number} | letter: {self.letter} | exists: {self.exists} | list: {self.list}'
        )

    def set_letter(self, letter: str):
        db.Players.update_one(
            {'_id': self._id}, {'$set': {'letter': letter}}, upsert=False
        )
        logger.info(
            f'fn > Player set letter > OK | _id: {self._id} | letter: {self.letter}'
        )

    def eliminate(self):
        db.Players.update_one(
            {'_id': self._id},
            {
                '$set': {
                    'alive': False,
                    'letter': '',
                    'deathCouncilNumber': get_council_number(),
                }
            },
            upsert=False,
        )
        logger.info(
            f'fn > Player elimination > OK | _id: {self._id} | alive: {self.alive} | letter: '''
        )

    def resurrect(self):
        db.Players.update_one(
            {'_id': self._id},
            {
                '$set': {
                    'alive': True,
                    'letter': '',
                    'deathCouncilNumber': 0,
                    'lastWishExpressed': False,
                }
            },
            upsert=False,
        )
        logger.info(
            f'fn > Player resurrection > OK | _id: {self._id} | alive: {self.alive} | letter: '''
        )

    def express_last_wish(self):
        db.Players.update_one(
            {'_id': self._id}, {'$set': {'lastWishExpressed': True}}, upsert=False
        )
        logger.info(
            f'fn > Player last wish expression > OK | _id: {self._id} | lastWishExpressed: True'
        )


class Variables:

    def open_joining() -> None:
        db.Variables.update_one({'id': 0}, {'$set': {'state': 0}}, upsert=False)
        logger.info('fn > Variables start game > OK | state: 1')

    def start_game() -> None:
        db.Variables.update_one({'id': 0}, {'$set': {'state': 1}}, upsert=False)
        logger.info('fn > Variables start game > OK | state: 1')

    def wait_for_last_vote() -> None:
        db.Variables.update_one({'id': 0}, {'$set': {'state': 2}}, upsert=False)
        logger.info('fn > Variables wait for last vote > OK | state: 2')

    def start_last_vote() -> None:
        db.Variables.update_one({'id': 0}, {'$set': {'state': 3}}, upsert=False)
        logger.info('fn > Variables start last vote > OK | state: 3')

    def game_end() -> None:
        db.Variables.update_one({'id': 0}, {'$set': {'state': 4}}, upsert=False)
        logger.info('fn > Variables game end > OK | state: 4')

    def get_state() -> int:
        return db.Variables.find_one({'id': 0}).get('state', 0)

    def set_vote_msg_id(id: int) -> None:
        db.Variables.update_one(
            {'id': 0}, {'$set': {'voteMessageId': id}}, upsert=False
        )
        logger.info(f'fn > Variables set vote msg id > OK | id: {id}')

    def set_last_winner_id(id: discord.User.id) -> None:
        db.Variables.update_one({'id': 0}, {'$set': {'lastWinnerId': id}}, upsert=False)
        logger.info(f'fn > Variables set last winner id > OK | discord id: {id}')

    def set_btn_how_to_alliance_msg_id(id: discord.Message.id) -> None:
        db.Variables.update_one(
            {'id': 0}, {'$set': {'btnHowToAllianceMsgId': id}}, upsert=False
        )
        logger.info(f'fn > Variables set btn how to alliance msg id > OK | id: {id}')

    def set_immunite_collar_msg_id(id: discord.Message.id) -> None:
        db.Variables.update_one(
            {'id': 0}, {'$set': {'immuniteCollarMsgId': id}}, upsert=False
        )
        logger.info(f'fn > Variables set immunite collar msg id > OK | id: {id}')

    def set_immunite_collar_player_id(id):
        db.Variables.update_one(
            {'id': 0}, {'$set': {'immuniteCollarPlayerId': id}}, upsert=False
        )
        logger.info(f'fn > Variables set immunite collar player id > OK | id: {id}')

    def get_immunite_collar_msg_id() -> int:
        return db.Variables.find_one({'id': 0}).get('immuniteCollarMsgId', 0)

    def get_immunite_collar_player_id() -> int:
        return db.Variables.find_one({'id': 0}).get('immuniteCollarPlayerId', 0)

    def get_vote_msg_id() -> int:
        return db.Variables.find_one({'id': 0}).get('voteMessageId', 0)

    def get_last_winner_id() -> int:
        return db.Variables.find_one({'id': 0}).get('lastWinnerId')

    def get_guild_id() -> int:
        return db.Variables.find_one({'id': 0}).get('guildId', 0)

    def get_token() -> int:
        return db.Variables.find_one({'id': 0}).get('token', 0)

    def get_btn_how_to_alliance_msg_id() -> str:
        return db.Variables.find_one({'id': 0}).get('btnHowToAllianceMsgId', None)


class NewAlliance:
    def __init__(self, **kwargs):
        self.text_id = kwargs.get('text_id', 0)
        self.voice_id = kwargs.get('voice_id', 0)
        self.name = kwargs.get('name', 'unknown')
        self.creator = kwargs.get('creator', '')

    def save(self) -> None:
        db.Alliances.insert_one(
            {
                'text_id': self.text_id,
                'voice_id': self.voice_id,
                'name': self.name,
                'members': [ObjectId(str(self.creator))],
            }
        )
        logger.info(
            f'fn > NewPlayer saving > OK | Text id: {self.text_id} | Voice id: {self.voice_id} | Creator db _id: {self.creator}'
        )


class Alliance:
    def __init__(self, **kwargs):
        logger.info(f'AllianceObjectCreation | args: {kwargs}')
        self.text_id = kwargs.get('text_id', 0)
        self.voice_id = 0
        self.name = kwargs.get('name', 'unknown')
        self.exists = False
        self.members = []
        self.list = []
        self.alliance = None
        self._id = 0
        self.find()

    def find(self):
        if self.text_id != 0:
            self.alliance = db.Alliances.find_one(filter={'text_id': self.text_id})
            if self.alliance is not None:
                self.voice_id = self.alliance.get('voice_id', 0)
                self.name = self.alliance.get('name', 'unknown')
                self.members = self.alliance.get('members', [])
                self._id = self.alliance.get('_id', 0)
                self.exists = True
                logger.info(
                    f'fn > Alliance find > OK | text_id: {self.text_id} | voice_id: {self.voice_id} | _id: {self._id} | members: {self.members} | exists: {self.exists}'
                )
            else:
                logger.error(
                    f'fn > AllianceNotFound | text_id: {self.text_id} | members: {self.members}'
                )
        elif self.name != 'unknown':
            self.alliance = db.Alliances.find_one(filter={'name': self.name})
            if self.alliance is not None:
                self.text_id = self.alliance.get('text_id', 0)
                self.voice_id = self.alliance.get('voice_id', 0)
                self.members = self.alliance.get('members', [])
                self._id = self.alliance.get('_id', 0)
                self.exists = True
                logger.info(
                    f'fn > Alliance find > OK | text_id: {self.text_id} | voice_id: {self.voice_id} | _id: {self._id} | members: {self.members} | exists: {self.exists}'
                )
            else:
                logger.error(
                    f'fn > AllianceNotFound | text_id: {self.text_id} | members: {self.members}'
                )

    def add_member(self, _id: int):
        self.members.append(ObjectId(str(_id)))
        db.Alliances.update_one(
            {'_id': self._id}, {'$set': {'members': self.members}}, upsert=False
        )
        logger.info(
            f'fn > Alliance add member > OK | Alliance _id: {self._id} | Member _id: {_id} | Members: {self.members}'
        )

    def remove_member(self, _id: int):
        self.members.remove(ObjectId(str(_id)))
        db.Alliances.update_one(
            {'_id': self._id}, {'$set': {'members': self.members}}, upsert=False
        )
        logger.info(
            f'fn > Alliance remove member > OK | Alliance _id: {self._id} | Member _id: {_id} | Members: {self.members}'
        )

    def close(self, user):
        db.Alliances.update_one(
            {'_id': self._id}, {'$set': {'members': []}}, upsert=False
        )
        if user:
            logger.info(
                f'fn > Alliance closing > OK | Alliance _id: {self._id} | Member: {user} (id: {user.id})'
            )
        else:
            logger.info(
                f'fn > Alliance closing > OK | Alliance _id: {self._id} | By the bot'
            )

    def delete(self, user):
        db.Alliances.delete_one({'_id': self._id})
        logger.info(
            f'fn > Alliance deletion > OK | Alliance _id: {self._id} | Member: {user} (id: {user.id})'
        )

    def purge_empty_alliances(self):
        self.result = db.Alliances.delete_many({'members': []})
        logger.info(
            f'fn > Empty Alliances Purge > OK | count: {self.result.deleted_count}'
        )

    def rename(self, name: str) -> None:
        db.Alliances.update_one(
            {'_id': self._id}, {'$set': {'name': name}}, upsert=False
        )
        logger.info(
            f'fn > Alliance renamation > OK | Alliance _id: {self._id} | Old name : {self.name} | New name : {name}'
        )


class NewVoteLog:
    def __init__(self, **kwargs):
        self.votes = kwargs.get('votes', None)
        self.eliminated = kwargs.get('eliminated', None)
        self.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.votes_logs = db.VoteLog
        self.number = get_council_number() + 1
        self.players_list = Player(option='living').list
        self.voters_number = len(self.players_list)
        self.cheaters_number = kwargs.get('cheaters_number', 0)
        self.tied_players = kwargs.get('tied_players', [])
        self.votes_list = []
        for v in self.votes:
            self.votes_list.append(
                {
                    'voter': Player(id=v)._id,
                    'for': Player(
                        letter=chr(EMOJIS_LIST.index(self.votes[v][0]) + 65)
                    )._id,
                }
            )
        if self.eliminated:
            self.eliminated_dict = [{'_id': el._id} for el in self.eliminated]
        else:
            self.eliminated_dict = []
        if self.tied_players:
            self.tied_players = [{'_id': el._id} for el in self.tied_players]

    def save(self):
        self.alliance_number = get_alliances_number()
        db.VoteLog.insert_one(
            {
                'votes': self.votes_list,
                'date': self.date,
                'number': self.number,
                'eliminated': self.eliminated_dict,
                'votersNumber': self.voters_number,
                'cheatersNumber': self.cheaters_number,
                'tied_players': self.tied_players,
                'alliance_number': self.alliance_number,
            }
        )
        logger.info(
            f'fn > NewVoteLog saving > OK | votes: {self.votes_list} | date: {self.date} | number: {self.number} | eliminated: {self.eliminated_dict} | voters_number: {self.voters_number} | cheaters_number: {self.cheaters_number} | tied_players {self.tied_players} | alliance_number: {self.alliance_number}'
        )


class VoteLog:
    def __init__(self, **kwargs):
        logger.info(f'VoteLogObjectCreation | args: {kwargs}')
        self._id = kwargs.get('_id', None)
        self.number = kwargs.get('number', None)
        self.date = kwargs.get('date', None)
        self.eliminated = []
        self.votes = []
        self.last = kwargs.get('last', False)
        self.is_last_vote = False
        self.voters_number = None
        self.cheaters_number = None
        self.tied_players = []
        self.alliance_number = None
        self.vote_log = None
        if self.last is True:
            self.last = 0
        self.find()

    def find(self):
        if self._id is not None:
            self.vote_log = db.VoteLog.find_one(filter={'_id': self._id})
        elif self.number is not None:
            self.vote_log = db.VoteLog.find_one(filter={'number': self.number})
        elif self.date is not None:
            self.vote_log = db.VoteLog.find_one(filter={'date': self.date})
        elif not (self.last is False):
            self.vote_log = db.VoteLog.find_one(
                filter={'number': get_council_number() + self.last}
            )
        if self.vote_log:
            self._id = self.vote_log.get('_id', None) if not self._id else self._id
            self.number = (
                self.vote_log.get('number', None) if not self.number else self.number
            )
            self.date = self.vote_log.get('date', None) if not self.date else self.date
            self.votes = self.vote_log.get('votes', None)
            self.voters_number = self.vote_log.get('votersNumber', None)
            self.cheaters_number = self.vote_log.get('cheatersNumber', None)
            self.eliminated_dict = self.vote_log.get('eliminated', [])
            self.tied_players = self.vote_log.get('tied_players', [])
            self.alliance_number = self.vote_log.get('alliance_number', None)
            if self.eliminated_dict != []:
                self.eliminated = [
                    Player(_id=ObjectId(el['_id'])) for el in self.eliminated_dict
                ]
            if self.number == get_council_number():
                self.is_last_vote = True
            logger.info(f'fn > Vote Log find > OK | log: {self.vote_log}')

    def update_eliminated(self, eliminated):
        if isinstance(eliminated, list):
            eliminated = [eliminated]
        for el in eliminated:
            self.eliminated.append({'_id': el._id})
        db.VoteLog.update_one(
            {'_id': self._id}, {'$set': {'eliminated': self.eliminated}}, upsert=False
        )
        logger.info(
            f'fn > Vote Log eliminated update > OK | _id: {self._id} | eliminated: {eliminated}'
        )


def get_council_number():
    return db.VoteLog.count_documents({})


def get_alliances_number():
    return db.Alliances.count_documents({})


def delete_all_vote_logs() -> None:
    db.VoteLog.delete_many({})
