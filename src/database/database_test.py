import unittest
from .player import PlayerData, Player, PlayerList, db
from bson.objectid import ObjectId
from ..utils.models import get_council_number

class TestDatabasePlayerData(unittest.TestCase):

    def test_player_data(self):
        player = PlayerData({
            '_id': 1,
            'id': 1,
            'nickname': 'nickname',
            'alive': True,
            'letter': 'A',
            'lastWishExpressed': True,
            'deathCouncilNumber': 1
        })
        self.assertEqual(player._id, 1)
        self.assertEqual(player.id, 1)
        self.assertEqual(player.nickname, 'nickname')
        self.assertEqual(player.alive, True)
        self.assertEqual(player.letter, 'A')
        self.assertEqual(player.last_wish_expressed, True)
        self.assertEqual(player.death_council_number, 1)

class TestDatabasePlayer(unittest.TestCase):

    def test_player_by__id(self):
        player = Player(_id=ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by__id(self):
        player = Player(id=889125377509851216)
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by_nickname(self):
        player = Player(nickname='Arthur D')
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by_letter(self):
        player = Player(letter='')
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by_death_council_number(self):
        player = Player(deathCouncilNumber=0)
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by_alive(self):
        player = Player(alive=True)
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by_last_wish_expressed(self):
        player = Player(lastWishExpressed=False)
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_by_data(self):
        player = Player({
            '_id': ObjectId('65b90e7990bf8da491b1ff0c'),
            'id': 889125377509851216,
            'nickname': 'Arthur D',
            'alive': True,
            'letter': '',
            'lastWishExpressed': False,
            'deathCouncilNumber': 0
        })
        self.assertEqual(player.object._id, ObjectId('65b90e7990bf8da491b1ff0c'))
        self.assertEqual(player.object.id, 889125377509851216)
        self.assertEqual(player.object.nickname, 'Arthur D')
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_resurrect(self):
        player = Player({
            '_id': ObjectId('65b90e7990bf8da491b1ff0c'),
            'id': 889125377509851216,
            'nickname': 'Arthur D',
            'alive': True,
            'letter': '',
            'lastWishExpressed': False,
            'deathCouncilNumber': 0
        })
        player.resurrect()
        self.assertEqual(player.object.alive, True)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.death_council_number, 0)
        self.assertEqual(player.object.last_wish_expressed, False)

    def test_player_eliminate(self):
        player = Player({
            '_id': ObjectId('65b90e7990bf8da491b1ff0c'),
            'id': 889125377509851216,
            'nickname': 'Arthur D',
            'alive': True,
            'letter': '',
            'lastWishExpressed': False,
            'deathCouncilNumber': 0
        })
        player.eliminate()
        self.assertEqual(player.object.alive, False)
        self.assertEqual(player.object.letter, '')
        self.assertEqual(player.object.death_council_number, db.VoteLog.count_documents({}))

class TestDatabasePlayerList(unittest.TestCase):

    def test_player_list(self):
        players = PlayerList(alive=True)
        self.assertEqual(len(players.objects) > 0, True)
        self.assertEqual(type(players.objects[0]), Player)
        self.assertEqual(type(players.objects[0].object), PlayerData)

if __name__ == '__main__':
    unittest.main()
