from datetime import datetime

import dns.resolver
from bson.objectid import ObjectId
from dotenv import load_dotenv  # for python-dotenv method
from pymongo.mongo_client import MongoClient

load_dotenv()                    #for python-dotenv method
from os import environ

from utils.logging import get_logger

logger = get_logger(__name__)
client = None
db = None

def setup_db_connection():
	global client, db
	logger.info("Connection to MongoDb...")
	dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
	dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

	# Create a new client and connect to the server
	client = MongoClient(environ.get("MongoDB_URI"))
	db = client.Game

	try:
		client.admin.command('ping')
		logger.info("Connected to MongoDb")
	except Exception as e:
		logger.error("Connection to MongoDb FAILED")
		logger.error(e)
		
class NewPlayer:
	
	def __init__(self,**kwargs):
		self.id = kwargs.get("id", 0)
		self.nickname = kwargs.get("nickname", "unknown")
		self.alive = kwargs.get("alive", True)
		self.letter = kwargs.get("letter", "")
		self.death_council_number = kwargs.get("dcn", 0)
	
	def save(self) -> None:
		db.Players.insert_one({"id": self.id,"nickname": self.nickname,"alive": self.alive,"deathCouncilNumber": self.death_council_number,"letter":self.letter})
		logger.info(f"fn > NewPlayer saving > OK | Discord id: {self.id} | Nickname: {self.nickname}")

class Player:
	
	def __init__(self,**kwargs):
		logger.info(f"PlayerObjectCreation | args: {kwargs}")
		self.id = kwargs.get("id", 0)
		self.nickname = kwargs.get("nickname", "unknown")
		self.alive = kwargs.get("alive", True)
		self.death_council_number = kwargs.get("dcn", 0)
		self.option = kwargs.get("option", "unknown")
		self.letter = kwargs.get("letter", "")
		self._id = None
		self.exists = False
		self.list = []
		
		self.find()
	
	def find(self):
		if self.id != 0:
			self.player = db.Players.find_one(filter={"id":self.id})
			if self.player != None:
				self.nickname = self.player.get("nickname", "unknown")
				self.alive = self.player.get("alive", True)
				self.death_council_number = self.player.get("deathCouncilNumber", 0)
				self.letter = self.player.get("letter", "")
				self._id = self.player.get("_id", None)
				self.exists = True
		elif self.nickname != "unknown":
			self.player = db.Players.find_one(filter={"nickname":self.nickname})
			if self.player != None:
				self.id = self.player.get("id", 0)
				self.alive = self.player.get("alive", True)
				self.death_council_number = self.player.get("deathCouncilNumber", 0)
				self.letter = self.player.get("letter", "")
				self._id = self.player.get("_id", None)
				self.exists = True
		elif self.letter != "":
			self.player = db.Players.find_one(filter={"letter":self.letter})
			if self.player != None:
				self.id = self.player.get("id", 0)
				self.nickname = self.player.get("nickname", "unknown")
				self.alive = self.player.get("alive", True)
				self.death_council_number = self.player.get("deathCouncilNumber", 0)
				self._id = self.player.get("_id", None)
				self.exists = True
		elif self.option == "living":
			self.list = list(db.Players.find({"alive":True}))
		elif self.option == "eliminated":
			self.list = list(db.Players.find({"alive":False}))
		logger.info(f"fn > Player find > OK | player: {self.player} | id: {self.id} | _id: {self._id} | nickname: {self.nickname} | alive: {self.alive} | dCN: {self.death_council_number} | letter: {self.letter} | exists: {self.exists} | list: {self.list}")
	
	def set_letter(self,letter: str):
		db.Players.update_one({"_id": self._id},{"$set": {"letter":letter}}, upsert=False)
		logger.info(f"fn > Player set letter > OK | _id: {self._id} | letter: {self.letter}")

	def eliminate(self):
		db.Players.update_one({"_id": self._id},{"$set": {"alive":False,"letter":""}}, upsert=False)
		logger.info(f"fn > Player elimination > OK | _id: {self._id} | alive: {self.alive} | letter: \"\"")

class Variables:
	
	def start_game() -> None:
		db.Variables.update_one({"id": 0},{"$set": {"state":1}}, upsert=False)
		logger.info(f"fn > Variables start game > OK | state: 1")

	def wait_for_last_vote() -> None:
		db.Variables.update_one({"id": 0},{"$set": {"state":2}}, upsert=False)
		logger.info(f"fn > Variables wait for last vote > OK | state: 2")

	def start_last_vote() -> None:
		db.Variables.update_one({"id": 0},{"$set": {"state":3}}, upsert=False)
		logger.info(f"fn > Variables start last vote > OK | state: 3")

	def game_end() -> None:
		db.Variables.update_one({"id": 0},{"$set": {"state":4}}, upsert=False)
		logger.info(f"fn > Variables game end > OK | state: 4")

	def get_state() -> int:
		return db.Variables.find_one({"id":0}).get("state", 0)
	
	def set_vote_msg_id(id: int) -> None:
		db.Variables.update_one({"id": 0},{"$set": {"voteMessageId":id}}, upsert=False)
		logger.info(f"fn > Variables set vote msg id > OK | id: {id}")
		
	def set_last_vote_date(date: str) -> None:
		db.Variables.update_one({"id": 0},{"$set": {"lastVoteDate":date}}, upsert=False)
		logger.info(f"fn > Variables set last vote date > OK | date: {date}")

	def get_last_vote_date() -> str:
		return db.Variables.find_one({"id":0}).get("lastVoteDate", None)

	def get_vote_msg_id() -> int:
		return db.Variables.find_one({"id":0}).get("voteMessageId", 0)
	
	def get_guild_id() -> int:
		return db.Variables.find_one({"id":0}).get("guildId", 0)
	
	def get_token() -> int:
		return db.Variables.find_one({"id":0}).get("token", 0)

class NewAlliance:
	
	def __init__(self,**kwargs):
		self.text_id = kwargs.get("text_id", 0)
		self.voice_id = kwargs.get("voice_id", 0)
		self.name = kwargs.get("name", "unknown")
		self.creator = kwargs.get("creator", "")
	
	def save(self) -> None:
		db.Alliances.insert_one({"text_id": self.text_id,"voice_id":self.voice_id,"name": self.name,"members": [ObjectId(str(self.creator))]})
		logger.info(f"fn > NewPlayer saving > OK | Text id: {self.text_id} | Voice id: {self.voice_id} | Creator db id: {self.creator}")
		
class Alliance:
	
	def __init__(self,**kwargs):
		logger.info(f"AllianceObjectCreation | args: {kwargs}")
		self.text_id = kwargs.get("text_id", 0)
		self.voice_id = 0
		self.name = "unknown"
		self.exists = False
		self.members = kwargs.get("members", [])
		self._id = 0
		self.find()
	
	def find(self):
		self.alliance = db.Alliances.find_one(filter={"text_id":self.text_id})
		if self.alliance != None:
			self.voice_id = self.alliance.get("voice_id", 0)
			self.name = self.alliance.get("name", "unknown")
			self.members = self.alliance.get("members", [])
			self._id = self.alliance.get("_id", 0)
			self.exists = True
			logger.info(f"fn > Player find > OK | text_id: {self.text_id} | voice_id: {self.voice_id} | _id: {self._id} | members: {self.members} | exists: {self.exists}")
		else:
			logger.error(f"fn > PlayerNotFound | text_id: {self.text_id} | members: {self.members}")

	def add_member(self,_id: int):
		self.members.append(ObjectId(str(_id)))
		db.Alliances.update_one({"_id": self._id},{"$set": {"members":self.members}}, upsert=False)
		logger.info(f"fn > Alliance add member > OK | Alliance _id: {self._id} | Member _id: {_id} | Members: {self.members}")

	def remove_member(self,_id: int):
		self.members.remove(ObjectId(str(_id)))
		db.Alliances.update_one({"_id": self._id},{"$set": {"members":self.members}}, upsert=False)
		logger.info(f"fn > Alliance remove member > OK | Alliance _id: {self._id} | Member _id: {_id} | Members: {self.members}")

# TODO alliance log : member, council number of join, council number of leave, add_by

class NewVoteLog:# XXX Continuer NewVoteLog
	def __init__(self,**kwargs):
		self.votes = kwargs.get("votes", None)
		self.eliminated_discord_id = kwargs.get("eliminated", None)
		self.date = datetime.now().strftime("%d/%m/%Y")
		self.votes_logs = db.VoteLogs
		self.number = len(self.votes_logs.list_indexes()) + 1 
		self.players_list = db.Players.list_indexes()
		self.eliminated_db_id = None
		
	def save(self):
		db.Alliances.insert_one({
			"votes": self.votes,
			"date": self.date,
			"number": self.number,
			"eliminated": [ObjectId(str(self.eliminated_db_id))]
		})

class VoteLog:
	def __init__(self, **kwargs):
		self._id = kwargs.get("_id",None)
		self.number = kwargs.get("number",None)
		self.date = kwargs.get("date",None)
		self.votes = self.filter = {}
		self.find()
	
	def find(self):
		if self._id != None:
			self.filter = {"_id":self._id}
		elif self.number != 0:
			self.filter = {"number":self.number}
		elif self.date != 0:
			self.filter = {"filter":self.filter}
		self.vote_log = db.VoteLogs.find_one(filter=self.filter)
		if self.vote_log:
			self._id = self.vote_log.get("_id",None) if not self._id else self._id
			self.number = self.vote_log.get("number",None) if not self.number else self.number
			self.date = self.vote_log.get("date",None) if not self.date else self.date
			self.votes = self.vote_log.get("votes",None)