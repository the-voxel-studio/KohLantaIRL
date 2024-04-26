import unittest

from bson.objectid import ObjectId

from .alliance import Alliance, AllianceData
from .database import db
from .game import Game
from .player import Player, PlayerData, PlayerList
from .votelog import VoteLog, VoteLogData, VoteLogList

player_data = db.Players.find_one({})
player_data['id'] = int(player_data['id'])
alliance_data = db.Alliances.find_one({})
votelog_data = db.VoteLog.find_one({})
game_data = db.Game.find_one({})


class TestDatabasePlayerData(unittest.TestCase):

    def test_player_data(self):
        player = PlayerData(player_data)
        self.assertEqual(player._id, player_data['_id'])
        self.assertEqual(player.id, player_data['id'])
        self.assertEqual(player.nickname, player_data['nickname'])
        self.assertEqual(player.alive, player_data['alive'])
        self.assertEqual(player.letter, player_data['letter'])
        self.assertEqual(player.last_wish_expressed, player_data['last_wish_expressed'])
        self.assertEqual(player.death_council_number, player_data['death_council_number'])


class TestDatabasePlayer(unittest.TestCase):

    def test_player_by__id(self):
        player = Player(_id=player_data['_id'])
        self.assertEqual(player.object._id, player_data['_id'])
        self.assertEqual(player.object.id, player_data['id'])
        self.assertEqual(player.object.nickname, player_data['nickname'])
        self.assertEqual(player.object.alive, player_data['alive'])
        self.assertEqual(player.object.death_council_number, player_data['death_council_number'])
        self.assertEqual(player.object.letter, player_data['letter'])
        self.assertEqual(player.object.last_wish_expressed, player_data['last_wish_expressed'])

    def test_player_by_id(self):
        player = Player(id=player_data['id'])
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)

    def test_player_by_nickname(self):
        player = Player(nickname=player_data['nickname'])
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)

    def test_player_by_letter(self):
        player = Player(letter=player_data['letter'])
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)

    def test_player_by_death_council_number(self):
        player = Player(death_council_number=player_data['death_council_number'])
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)

    def test_player_by_alive(self):
        player = Player(alive=player_data['alive'])
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)

    def test_player_by_last_wish_expressed(self):
        player = Player(last_wish_expressed=player_data['last_wish_expressed'])
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)

    def test_player_by_data(self):
        player = Player(data=player_data)
        self.assertEqual(type(player.object._id), ObjectId)
        self.assertEqual(type(player.object.id), int)
        self.assertEqual(type(player.object.nickname), str)
        self.assertEqual(type(player.object.alive), bool)
        self.assertEqual(type(player.object.death_council_number), int)
        self.assertEqual(type(player.object.letter), str)
        self.assertEqual(type(player.object.last_wish_expressed), bool)


class TestDatabasePlayerList(unittest.TestCase):

    def test_player_list(self):
        players = PlayerList(alive=True)
        self.assertEqual(len(players.objects) > 0, True)
        self.assertEqual(type(players.objects[0].object), PlayerData)


class TestDatabaseAllianceData(unittest.TestCase):

    def test_alliance_data(self):
        alliance = AllianceData(alliance_data)
        self.assertEqual(alliance._id, alliance_data['_id'])
        self.assertEqual(alliance.text_id, alliance_data['text_id'])
        self.assertEqual(alliance.voice_id, alliance_data['voice_id'])
        self.assertEqual(alliance.name, alliance_data['name'])
        self.assertEqual(alliance.members.objects[0].object.__dict__, Player(_id=alliance_data['members'][0]).object.__dict__)


class TestDatabaseAlliance(unittest.TestCase):

    def test_alliance_by__id(self):
        alliance = Alliance(_id=alliance_data['_id'])
        self.assertEqual(alliance.object._id, alliance_data['_id'])
        self.assertEqual(alliance.object.text_id, alliance_data['text_id'])
        self.assertEqual(alliance.object.voice_id, alliance_data['voice_id'])
        self.assertEqual(alliance.object.name, alliance_data['name'])
        self.assertEqual(type(alliance.object.members), PlayerList)

    def test_alliance_by_text_id(self):
        alliance = Alliance(text_id=alliance_data['text_id'])
        self.assertEqual(alliance.object._id, alliance_data['_id'])
        self.assertEqual(alliance.object.text_id, alliance_data['text_id'])
        self.assertEqual(alliance.object.voice_id, alliance_data['voice_id'])
        self.assertEqual(alliance.object.name, alliance_data['name'])
        self.assertEqual(type(alliance.object.members), PlayerList)

    def test_alliance_by_voice_id(self):
        alliance = Alliance(voice_id=alliance_data['voice_id'])
        self.assertEqual(alliance.object._id, alliance_data['_id'])
        self.assertEqual(alliance.object.text_id, alliance_data['text_id'])
        self.assertEqual(alliance.object.voice_id, alliance_data['voice_id'])
        self.assertEqual(alliance.object.name, alliance_data['name'])
        self.assertEqual(type(alliance.object.members), PlayerList)

    def test_alliance_by_name(self):
        alliance = Alliance(name=alliance_data['name'])
        self.assertEqual(alliance.object._id, alliance_data['_id'])
        self.assertEqual(alliance.object.text_id, alliance_data['text_id'])
        self.assertEqual(alliance.object.voice_id, alliance_data['voice_id'])
        self.assertEqual(alliance.object.name, alliance_data['name'])
        self.assertEqual(type(alliance.object.members), PlayerList)

    def test_alliance_by_data(self):
        alliance = Alliance(data=alliance_data)
        self.assertEqual(alliance.object.text_id, alliance_data['text_id'])
        self.assertEqual(alliance.object.voice_id, alliance_data['voice_id'])
        self.assertEqual(alliance.object.name, alliance_data['name'])
        self.assertEqual(type(alliance.object.members), PlayerList)
        self.assertEqual(alliance.object.members.objects[0].object.__dict__, Player(_id=alliance_data['members'][0]).object.__dict__)


class TestDatabaseVoteLogData(unittest.TestCase):

    def test_alliance_data(self):
        votelog = VoteLogData(votelog_data)
        self.assertEqual(votelog._id, votelog_data['_id'])
        self.assertEqual(votelog.number, votelog_data['number'])
        self.assertEqual(votelog.date, votelog_data['date'])
        self.assertEqual(votelog.eliminated.objects[0].object.__dict__, Player(_id=votelog_data['eliminated'][0]['_id']).object.__dict__)
        self.assertEqual(votelog.votes[0]['voter'].object.__dict__, Player(_id=votelog_data['votes'][0]['voter']).object.__dict__)
        self.assertEqual(votelog.votes[0]['for'].object.__dict__, Player(_id=votelog_data['votes'][0]['for']).object.__dict__)
        self.assertEqual(votelog.voters_number, votelog_data['voters_number'])
        self.assertEqual(votelog.cheaters_number, votelog_data['cheaters_number'])
        self.assertEqual(type(votelog.tied_players), PlayerList)
        self.assertEqual(votelog.alliance_number, votelog_data['alliance_number'])


class TestDatabaseVoteLog(unittest.TestCase):

    def test_votelog_by__id(self):
        votelog = VoteLog(_id=votelog_data['_id'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_number(self):
        votelog = VoteLog(number=votelog_data['number'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_date(self):
        votelog = VoteLog(date=votelog_data['date'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_eliminated(self):
        votelog = VoteLog(eliminated=votelog_data['eliminated'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_votes(self):
        votelog = VoteLog(votes=votelog_data['votes'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_voters_number(self):
        votelog = VoteLog(voters_number=votelog_data['voters_number'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_cheaters_number(self):
        votelog = VoteLog(cheaters_number=votelog_data['cheaters_number'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_tied_players(self):
        votelog = VoteLog(tied_players=votelog_data['tied_players'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)

    def test_votelog_by_alliance_number(self):
        votelog = VoteLog(alliance_number=votelog_data['alliance_number'])
        self.assertEqual(type(votelog.object._id), ObjectId)
        self.assertEqual(type(votelog.object.number), int)
        self.assertEqual(type(votelog.object.date), str)
        self.assertEqual(type(votelog.object.eliminated.objects[0].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['voter'].object), PlayerData)
        self.assertEqual(type(votelog.object.votes[0]['for'].object), PlayerData)
        self.assertEqual(type(votelog.object.voters_number), int)
        self.assertEqual(type(votelog.object.cheaters_number), int)
        self.assertEqual(type(votelog.object.tied_players), PlayerList)
        self.assertEqual(type(votelog.object.alliance_number), int)


class TestDatabaseVoteLogList(unittest.TestCase):

    def test_player_list(self):
        votelogs = VoteLogList()
        self.assertEqual(len(votelogs.objects) > 0, True)
        self.assertEqual(type(votelogs.objects[0].object), VoteLogData)


class TestDatabaseGame(unittest.TestCase):

    def test_game_data(self):
        game = Game
        self.assertEqual(game.state, game_data['state'])
        self.assertEqual(game.vote_message_id, game_data['vote_message_id'])
        self.assertEqual(game.btn_how_to_alliance_msg_id, game_data['btn_how_to_alliance_msg_id'])
        self.assertEqual(game.last_winner_id, game_data['last_winner_id'])
        self.assertEqual(game.immunite_collar_msg_id, game_data['immunite_collar_msg_id'])
        self.assertEqual(game.immunite_collar_player_id, game_data['immunite_collar_player_id'])

    def test_game_data_modification(self):

        self.__backup_data = game_data
        game = Game

        game.state = self.__backup_data['state'] + 1
        game.vote_message_id = self.__backup_data['vote_message_id'] + 2
        game.btn_how_to_alliance_msg_id = self.__backup_data['btn_how_to_alliance_msg_id'] + 3
        game.last_winner_id = self.__backup_data['last_winner_id'] + 4
        game.immunite_collar_msg_id = self.__backup_data['immunite_collar_msg_id'] + 5
        game.immunite_collar_player_id = self.__backup_data['immunite_collar_player_id'] + 6

        self.assertEqual(game.state, game_data['state'] + 1)
        self.assertEqual(game.vote_message_id, game_data['vote_message_id'] + 2)
        self.assertEqual(game.btn_how_to_alliance_msg_id, game_data['btn_how_to_alliance_msg_id'] + 3)
        self.assertEqual(game.last_winner_id, game_data['last_winner_id'] + 4)
        self.assertEqual(game.immunite_collar_msg_id, game_data['immunite_collar_msg_id'] + 5)
        self.assertEqual(game.immunite_collar_player_id, game_data['immunite_collar_player_id'] + 6)

        game.state = self.__backup_data['state']
        game.vote_message_id = self.__backup_data['vote_message_id']
        game.btn_how_to_alliance_msg_id = self.__backup_data['btn_how_to_alliance_msg_id']
        game.last_winner_id = self.__backup_data['last_winner_id']
        game.immunite_collar_msg_id = self.__backup_data['immunite_collar_msg_id']
        game.immunite_collar_player_id = self.__backup_data['immunite_collar_player_id']


if __name__ == '__main__':
    unittest.main()
