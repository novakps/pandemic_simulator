import game
import unittest
from pprint import pprint

class Initialization(unittest.TestCase):
    def testInit(self):
        g = game.build_game()
        self.assertEquals([game.ATLANTA], g.research_stations)
        self.assertEquals(4, len(g.players))
        self.assertEquals(5, len([card for card in g.player_draw_pile if card == game.EPIDEMIC]))
        for player in g.players:
            self.assertEquals(2, len(player.cards))
            self.assertEquals(game.ATLANTA, player.location)
        self.assertEquals(48, len(g.cities))
        self.assertEquals(0, len(g.player_discard_pile))
        self.assertEquals(9, len(g.infection_discard_pile))

class Infection(unittest.TestCase):
    def testOutbreak(self):
        g = game.build_game()
        g.cities = {name: game.City(0, 0, 0, 0) for name in game.infection_cards.keys()}
        game.infect_city(g, 'london', game.BLACK, 3, [])
        game.infect_city(g, 'london', game.BLACK, 1, [])
        self.assertEquals(1, g.outbreaks)
        self.assertEquals(3, g.cities['london'].black)
        self.assertEquals(1, g.cities['essen'].black)
        self.assertEquals(1, g.cities['paris'].black)
        self.assertEquals(1, g.cities['new york'].black)
        self.assertEquals(1, g.cities['madrid'].black)
        game.infect_city(g, 'madrid', game.BLACK, 2, [])
        self.assertEquals(3, g.cities['madrid'].black)
        game.infect_city(g, 'madrid', game.BLACK, 1, [])
        self.assertEquals(3, g.outbreaks)
        self.assertEquals(3, g.cities['madrid'].black)
        self.assertEquals(3, g.cities['london'].black)
        self.assertEquals(3, g.cities['new york'].black)
        self.assertRaises(game.DefeatException, game.infect_city, g, 'new york', game.BLACK, 1, [])

    def testDiseaseLimit(self):
        g = game.build_game()
        g.cities = {name: game.City(0, 0, 0, 0) for name in game.infection_cards.keys()}
        for c in g.cities.keys()[:24]:
            game.infect_city(g, c, game.RED, 1, [])
            
        self.assertRaises(game.DefeatException, game.infect_city, g, g.cities.keys()[24], game.RED, 1, [])

        
                          
                              
        
    

if __name__=='__main__':
    unittest.main()
