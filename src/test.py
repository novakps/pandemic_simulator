import pandemic
import unittest
from pprint import pprint

class Initialization(unittest.TestCase):
    def testInit(self):
        g = pandemic.build_game()
        self.assertEquals([pandemic.ATLANTA], g.research_stations)
        self.assertEquals(4, len(g.players))
        self.assertEquals(5, len([card for card in g.player_draw_pile if card == pandemic.EPIDEMIC]))
        for player in g.players:
            self.assertEquals(2, len(player.cards))
            self.assertEquals(pandemic.ATLANTA, player.location)
        self.assertEquals(48, len(g.cities))
        self.assertEquals(0, len(g.player_discard_pile))
        self.assertEquals(9, len(g.infection_discard_pile))

class Infection(unittest.TestCase):
    def testOutbreak(self):
        g = pandemic.build_game()
        g.cities = {name: pandemic.City(0, 0, 0, 0) for name in pandemic.INFECTION_CARDS.keys()}
        pandemic.infect_city(g, 'london', pandemic.BLACK, 3, [])
        pandemic.infect_city(g, 'london', pandemic.BLACK, 1, [])
        self.assertEquals(1, g.outbreaks)
        self.assertEquals(3, g.cities['london'].black)
        self.assertEquals(1, g.cities['essen'].black)
        self.assertEquals(1, g.cities['paris'].black)
        self.assertEquals(1, g.cities['new york'].black)
        self.assertEquals(1, g.cities['madrid'].black)
        pandemic.infect_city(g, 'madrid', pandemic.BLACK, 2, [])
        self.assertEquals(3, g.cities['madrid'].black)
        pandemic.infect_city(g, 'madrid', pandemic.BLACK, 1, [])
        self.assertEquals(3, g.outbreaks)
        self.assertEquals(3, g.cities['madrid'].black)
        self.assertEquals(3, g.cities['london'].black)
        self.assertEquals(3, g.cities['new york'].black)
        self.assertRaises(pandemic.DefeatException, pandemic.infect_city, g, 'new york', pandemic.BLACK, 1, [])

    def testDiseaseLimit(self):
        g = pandemic.build_game()
        g.cities = {name: pandemic.City(0, 0, 0, 0) for name in pandemic.INFECTION_CARDS.keys()}
        for c in g.cities.keys()[:24]:
            pandemic.infect_city(g, c, pandemic.RED, 1, [])

        self.assertRaises(pandemic.DefeatException, pandemic.infect_city, g, g.cities.keys()[24], pandemic.RED, 1, [])







if __name__=='__main__':
    unittest.main()
