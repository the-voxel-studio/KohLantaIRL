from pymongo.mongo_client import MongoClient
import dns.resolver
from bson.objectid import ObjectId
from dotenv import load_dotenv   #for python-dotenv method
load_dotenv()                    #for python-dotenv method
from os import environ

print("Connection to MongoDb...")

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

# Create a new client and connect to the server
client = MongoClient(environ.get("MongoDB_URI"))
db = client.Game

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("OK")
except Exception as e:
    print("FAILED")
    print(e)
		
class NewPlayer:
	
	def __init__(self,**kwargs):
		self.id = kwargs.get("id", 0)
		self.nickname = kwargs.get("nickname", "unknown")
		self.alive = kwargs.get("alive", True)
		self.letter = kwargs.get("letter", "")
		self.death_council_number = kwargs.get("dcn", 0)
	
	def save(self) -> None:
		db.Players.insert_one({"id": self.id,"nickname": self.nickname,"alive": self.alive,"deathCouncilNumber": self.death_council_number,"letter":self.letter})

class Player:
	
	def __init__(self,**kwargs):
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
	
	def set_letter(self,letter: str):
		db.Players.update_one({"_id": self._id},{"$set": {"letter":letter}}, upsert=False)

	def eliminate(self):
		db.Players.update_one({"_id": self._id},{"$set": {"alive":False,"letter":""}}, upsert=False)
		
class Variables:
	
	def start_game() -> None:
		db.Variables.update_one({"id": 0},{"$set": {"state":1}}, upsert=False)

	def get_state() -> int:
		return db.Variables.find_one({"id":0}).get("state", 0)
	
	def set_vote_msg_id(id: int) -> None:
		db.Variables.update_one({"id": 0},{"$set": {"voteMessageId":id}}, upsert=False)
		
	def set_last_vote_date(date: str) -> None:
		db.Variables.update_one({"id": 0},{"$set": {"lastVoteDate":date}}, upsert=False)

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
		
class Alliance:
	
	def __init__(self,**kwargs):
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
			
	def add_member(self,_id: int):
		self.members.append(ObjectId(str(_id)))
		db.Alliances.update_one({"_id": self._id},{"$set": {"members":self.members}}, upsert=False)
	
	def remove_member(self,_id: int):
		self.members.remove(ObjectId(str(_id)))
		db.Alliances.update_one({"_id": self._id},{"$set": {"members":self.members}}, upsert=False)