import random
import traceback, sys
from collections import namedtuple, Counter
import pprint

DISPATCHER, MEDIC, OPERATIONS_EXPERT, RESEARCHER, SCIENTIST = roles = ['Dispatcher', 'Medic', 'Operations Expert', 'Researcher', 'Scientist']
MAX_RESEARCH_STATIONS = 6
OUTBREAK_LIMIT = 8
INFECTION_RATE_TRACK = [2, 2, 2, 3, 3, 4, 4]
YELLOW, BLUE, BLACK, RED = DISEASE_COLORS = ['yellow', 'blue', 'black', 'red']
CARDS_PER_PLAYER = {4:2, 3:3, 2:4}
HAND_LIMIT = 7
DISEASE_LIMIT = 24
EPIDEMIC = 'Epidemic'
OUTBREAK_TRIGGER = 3
ATLANTA = 'Atlanta'
INFECTION_CARDS = {ATLANTA: YELLOW,
                   'algiers': BLACK,
                   'baghdad': BLACK,
                   'bangkok': RED,
                   'beijing': RED,
                   'bogota': YELLOW,
                   'buenos aires': YELLOW,
                   'cairo': BLACK,
                   'chennai': BLACK,
                   'chicago': BLUE,
                   'delhi': BLACK,
                   'essen': BLUE,
                   'ho chi minh city': RED,
                   'hong kong': RED,
                   'istanbul': BLACK,
                   'jakarta': RED,
                   'johannesburg': YELLOW,
                   'karachi': BLACK,
                   'khartoum': YELLOW,
                   'kinshasa': YELLOW,
                   'kolkata': BLACK,
                   'lagos': YELLOW,
                   'lima': YELLOW,
                   'london': BLUE,
                   'los angeles': YELLOW,
                   'madrid': BLUE,
                   'manila': RED,
                   'mexico city': YELLOW,
                   'miami': YELLOW,
                   'milan': BLUE,
                   'moscow': BLACK,
                   'mumbai': BLACK,
                   'new york': BLUE,
                   'osaka': RED,
                   'paris': BLUE,
                   'riyadh': BLACK,
                   'san francisco': BLUE,
                   'santiago': YELLOW,
                   'sao paulo': YELLOW,
                   'seoul': RED,
                   'shanghai': RED,
                   'st. petersburg': BLUE,
                   'sydney': RED,
                   'taipei': RED,
                   'tehran': BLACK,
                   'tokyo': RED,
                   'toronto': BLUE,
                   'washington': BLUE}
SPECIAL_EVENTS = ['forecast', 'resilient population', 'government grant', 'one quiet night', 'airlift']
PLAYER_CARDS = INFECTION_CARDS.keys() + SPECIAL_EVENTS
assert len(PLAYER_CARDS) == 53

edges = [
    (ATLANTA, 'chicago'),
    (ATLANTA, 'washington'),
    (ATLANTA, 'miami'),
    ('algiers', 'madrid'),
    ('algiers', 'paris'),
    ('algiers', 'istanbul'),
    ('algiers', 'cairo'),
    ('baghdad', 'istanbul'),
    ('baghdad', 'tehran'),
    ('baghdad', 'karachi'),
    ('baghdad', 'riyadh'),
    ('baghdad', 'cairo'),
    ('bangkok', 'kolkata'),
    ('bangkok', 'hong kong'),
    ('bangkok', 'ho chi minh city'),
    ('bangkok', 'jakarta'),
    ('bangkok', 'chennai'),
    ('beijing', 'shanghai'),
    ('beijing', 'seoul'),
    ('bogota','miami'),
    ('bogota','sao paulo'),
    ('bogota','buenos aires'),
    ('bogota','lima'),
    ('bogota','mexico city'),
    ('buenos aires', 'sao paulo'),
    ('cairo', 'istanbul'),
    ('cairo', 'riyadh'),
    ('chennai', 'mumbai'),
    ('chennai', 'delhi'),
    ('chennai', 'kolkata'),
    ('chennai', 'jakarta'),
    ('chicago', 'toronto'),
    ('chicago', 'mexico city'),
    ('chicago', 'los angeles'),
    ('chicago', 'san francisco'),
    ('delhi', 'kolkata'),
    ('delhi', 'mumbai'),
    ('delhi', 'karachi'),
    ('delhi', 'tehran'),
    ('essen', 'st. petersburg'),
    ('essen', 'milan'),
    ('essen', 'paris'),
    ('essen', 'london'),
    ('ho chi minh city', 'hong kong'),
    ('ho chi minh city', 'manila'),
    ('ho chi minh city', 'jakarta'),
    ('hong kong', 'shanghai'),
    ('hong kong', 'taipei'),
    ('hong kong', 'manila'),
    ('hong kong', 'kolkata'),
    ('istanbul', 'st. petersburg'),
    ('istanbul', 'moscow'),
    ('istanbul', 'milan'),
    ('jakarta', 'sydney'),
    ('johannesburg', 'kinshasa'),
    ('johannesburg', 'khartoum'),
    ('karachi', 'tehran'),
    ('karachi', 'mumbai'),
    ('karachi', 'riyadh'),
    ('khartoum', 'kinshasa'),
    ('khartoum', 'lagos'),
    ('kinshasa', 'lagos'),
    ('lagos', 'sao paulo'),
    ('lima', 'mexico city'),
    ('lima', 'santiago'),
    ('london', 'madrid'),
    ('london', 'paris'),
    ('london', 'new york'),
    ('los angeles', 'san francisco'),
    ('los angeles', 'mexico city'),
    ('los angeles', 'sydney'),
    ('madrid', 'paris'),
    ('madrid', 'sao paulo'),
    ('madrid', 'new york'),
    ('manila', 'taipei'),
    ('manila', 'san francisco'),
    ('manila', 'sydney'),
    ('mexico city', 'miami'),
    ('milan', 'paris'),
    ('moscow', 'st. petersburg'),
    ('moscow', 'tehran'),
    ('new york', 'washington'),
    ('new york', 'toronto'),
    ('osaka', 'tokyo'),
    ('osaka', 'taipei'),
    ('san francisco', 'tokyo'),
    ('seoul', 'tokyo'),
    ('seoul', 'shanghai'),
    ('toronto', 'washington')     
    ] #89 edges?

ADJACENT_CITIES = {name:[] for name in INFECTION_CARDS.keys()}
for a,b in edges:
    ADJACENT_CITIES[a].append(b)
    ADJACENT_CITIES[b].append(a)

def build_game(players_count=4, difficulty_level=5):
    random.shuffle(roles)
    players = [Player(role, location=ATLANTA, cards=[]) for role in roles[:][:players_count]]

    #deal cards to players
    player_cards = PLAYER_CARDS[:]
    random.shuffle(player_cards)
    for i in range(CARDS_PER_PLAYER[players_count]):
        for player in players:
            player.cards.append(player_cards.pop(0))                    

    #prepare player draw pile
    player_draw_pile = []
    for i in range(difficulty_level, 0 , -1):
        split_point = len(player_cards) / i
        chunk = player_cards[:split_point]
        player_cards = player_cards[split_point:]
        chunk.append(EPIDEMIC)
        random.shuffle(chunk)
        player_draw_pile += chunk
    assert len(player_cards) == 0

    infection_draw_pile = INFECTION_CARDS.keys()
    random.shuffle(infection_draw_pile)

    cities = {name: City(0, 0, 0, 0) for name in INFECTION_CARDS.keys()}
    diseases = {color: Disease(color, cured=False, eradicated=False) for color in DISEASE_COLORS}
    game = Game(players=players,
                player_draw_pile=player_draw_pile,
                cities=cities,
                diseases=diseases,
                infection_draw_pile=infection_draw_pile,
                research_stations=[ATLANTA],
                outbreaks=0,
                infection_rate_marker=0)
    
    for i in range(3, 0 , -1):
        infect(game, 3, i)
    return game
             
def infect(game, rate, increment=1):
    for i in range(rate):
        game.infection_discard_pile.insert(0, game.infection_draw_pile.pop(0)) # first item in array is 'top' of pile
        city_name = game.infection_discard_pile[0]
        default_disease = INFECTION_CARDS[city_name]
        infect_city(game, city_name, default_disease, increment, [])
        
def infect_city(game, city_name, color, increment, ignore):
    city = game.cities[city_name]
    print 'infect_city', city_name, city, increment, ignore
    level = getattr(city, color)
    if level + increment > OUTBREAK_TRIGGER:
        game.cities[city_name] = city._replace(**{color:OUTBREAK_TRIGGER})
        outbreak(game, city_name, color, ignore)
    else:
        game.cities[city_name] = city._replace(**{color:level + increment})
        # check DISEASE_LIMIT
        if sum([getattr(city, color) for city in game.cities.values()]) > DISEASE_LIMIT:
            raise DefeatException('No {color} disease cubes left.'.format(color=color))         

def outbreak(game, city_name, color, ignore):
    print 'outbreak', city_name, ignore
    game.outbreaks += 1
    if game.outbreaks >= OUTBREAK_LIMIT:
        raise DefeatException('Outbreak limit reached')
    ignore.append(city_name)
    for adjacent_city in ADJACENT_CITIES[city_name]:
        if adjacent_city not in ignore:
            infect_city(game, adjacent_city, color, 1, ignore)

def epidemic(game):
    game.infection_rate_marker+=1
    game.infection_discard_pile.insert(0, game.infection_draw_pile.pop(-1)) # draw bottom card
    city_name = game.infection_discard_pile[0]
    default_disease = INFECTION_CARDS[city_name]
    infect_city(game, city_name, default_disease, 3, [])
    random.shuffle(game.infection_discard_pile)
    game.infection_draw_pile = game.infection_discard_pile + game.infection_draw_pile
    game.infection_discard_pile = []

def resilient_population(game, player):
    index = player.cards.index(RESILIENT_POPULATION)
    player.cards.pop(index) # removed from game

def government_grant(game, player, city):
    index = player.cards.index(GOVERNMENT_GRANT)
    assert city not in game.research_stations
    game.player_discard_pile.insert(0, player.cards.pop(index))

def one_quiet_night(game, player):
    index = player.cards.index(ONE_QUIET_NIGHT)
    game.next_infector_quiet = True
    game.player_discard_pile.insert(0, player.cards.pop(index))

def airlift(game, player, other_player, destination):
    index = player.cards.index(AIRLIFT)
    other_player.location = destination
    game.player_discard_pile.insert(0, player.pop(index))

def forecast(game, player, reordered_cards):
    index = player.cards.index(FORECAST)
    assert len(reordered_cards) == 6
    for i, card in enumerate(reordered_cards):
        game.infection_draw_pile[i] = card 
    game.player_discard_pile.insert(0, player.pop(index))

def drive(player, destination):
    print 'drive', player.role, destination
    assert destination in ADJACENT_CITIES[player.location]
    player.location = destination

def dispatcher_drive(player, other_player, destination):
    print 'dispatcher_drive', other_player.role, destination
    assert player.role == DISPATCHER
    assert destination in ADJACENT_CITIES[other_player.location]
    other_player.location = destination

def dispatcher_direct_flight(game, player, other_player, destination):
    'dispatcher_direct_flight', other_player.role, destination
    assert other_player.location != destination
    index = player.cards.index(destination) # raises exception if not found in list
    other_player.location = destination
    game.player_discard_pile.insert(0, player.cards.pop(index)) # insert as first item to 'top' of pile

def direct_flight(game, player, destination):
    print 'direct_flight', destination
    assert player.location != destination
    index = player.cards.index(destination) # raises exception if not found in list
    player.location = destination
    game.player_discard_pile.insert(0, player.cards.pop(index)) # insert as first item to 'top' of pile

def charter_flight(game, player, destination):
    print 'charter_flight', player.role, destination
    index = player.cards.index(player.location)
    player.location = destination
    game.player_discard_pile.insert(0, player.cards.pop(index)) #discard to 'top' of pile

def dispatcher_charter_flight(game, player, other_player, destination):
    print 'dispatcher_charter_flight', other_player.role, destination
    index = player.cards.index(other_player.location)
    other_player.location = destination
    game.player_discard_pile.insert(0, player.cards.pop(index)) # discard to top of pile

def shuttle_flight(game, player, destination):
    print 'shuttle_flight', player.role, destination
    assert player.location != destination
    assert player.location in game.research_stations
    assert destination in game.research_stations
    player.location = destination

def dispatcher_shuttle_flight(game, player, other_player, destination):
    print 'dispatcher_shuttle_flight', other_player.role, destination
    assert player.role == DISPATCHER
    shuttle_flight(game, other_player, destination)

def build_research_station(game, player, source_city=None):
    print 'build_research_station', player.location, 'from', source_city
    assert player.location not in game.research_stations
    if source_city:
        assert source_city in game.research_stations
        assert len(game.research_stations == MAX_RESEARCH_STATIONS)
        game.research_stations.remove(source_city)

    if player.role != OPERATIONS_EXPERT:
        index = player.cards.index(player.location)
        game.player_discard_pile.insert(0, player.cards.pop(index)) # discard to top of pile
    game.research_stations.append(player.location)
    assert len(game.research_stations) <= MAX_RESEARCH_STATIONS

def treat_disease(game, player, color):
    print 'treat_disease', player.role, color
    city = game.cities[player.location]
    infection_level = getattr(city, color)
    assert infection_level > 0
    disease = game.diseases[color]
    if disease.cured == True or player.role == MEDIC:
        infection_level = 0
    else:
        infection_level -= 1
    game.cities[player.location] = city._replace(**{color:infection_level})
    #eradication check
    if disease.cured == True:
        if len([city for city in game.cities if getattr(city, color) > 0])==0:
            print 'eradicated', color, '!'
            game.diseases[color] = diseases._replace(**{eradicated:True})

def share_knowledge(from_player, to_player, card):
    print 'share_knowledge', card, from_player.role, 'to', to_player.role
    assert from_player.location == to_player.location
    if from_player.role != RESEARCHER:
        assert card == from_player.location
    index = from_player.cards.index(card)
    to_player.cards.append(from_player.cards.pop(index))
    assert len(to_player.cards) <= HAND_LIMIT

def discover_cure(game, player, discard_cities):
    print 'discover_cure', discard_cities
    assert player.location in game.research_stations
    if (player.role == SCIENTIST):
        assert len(discard_cities) == 4
    else:
        assert len(discard_cities) == 5
    colors = {INFECTION_CARDS[city] for city in discard_cities}
    assert len(colors) == 1
    color = colors.pop()
    game.diseases[color] = game.diseases[color]._replace(**{'cured':True})
    for city in discard_cities:
        index = player.index(city)
        game.player_discard_pile.insert(0, player.cards.pop(index)) #always discard to top of pile

def draw_cards(game, player, count=2):
    if len(game.player_draw_pile) < count:
        raise DefeatException('Not enough cards in Player Draw Pile to continue')
    for i in range(count):
        player.cards.insert(0, game.player_draw_pile.pop(0))
        print 'draw_card:', player.cards[0]
        if EPIDEMIC == player.cards[0]:
            game.player_discard_pile.insert(0, player.cards.pop(0))
            epidemic(game)
    while len(player.cards) > HAND_LIMIT:
        discard_excess_card(game, player, player.choose_discard(game, player))

def random_discard(game, player):
    # or play special event card?
    return random.choice(player.cards)

def discard_excess_card(game, player, card):
    print 'discard_excess_card:', card, 'from', player
    index = player.cards.index(card)
    game.player_discard_pile.insert(0, player.cards.pop(index))

def do_nothing():
    print 'do_nothing'
    pass
  
City = namedtuple('City', DISEASE_COLORS)
Disease = namedtuple('Disease', ['color', 'cured', 'eradicated'])

class Player:
    tpl = '''{self.role} in {self.location}. Cards: {self.cards}'''
    def __init__(self, role, location, cards, choose_discard=random_discard):
        self.role = role
        self.location=location
        self.cards=cards
        self.choose_discard = choose_discard
    def __repr__(self):
        return self.tpl.format(self=self)

class Game:
    tpl = '''\tPlayers:
{players}
\tOutbreaks: {self.outbreaks}
\tResearch Stations: {self.research_stations}
\tInfection Rate: {infection_rate}
\tInfected Cities:
{cities}
\tDiseases:
{diseases}
Player Discard Pile:
{player_discard_pile}'''
    def __init__(self,
                 players,
                 player_draw_pile,
                 infection_draw_pile,
                 cities,
                 diseases,
                 research_stations,
                 outbreaks,
                 infection_rate_marker):
        self.players = players
        self.player_draw_pile = player_draw_pile
        self.player_discard_pile = []
        self.infection_draw_pile = infection_draw_pile
        self.infection_discard_pile = []
        self.research_stations = research_stations
        self.outbreaks = outbreaks
        self.infection_rate_marker = infection_rate_marker
        self.cities = cities
        self.diseases = diseases
        self.next_infector_quiet = False
        
    def infection_rate(self):
        return INFECTION_RATE_TRACK[self.infection_rate_marker]

    def __repr__(self):
        return self.tpl.format(self=self,
            players=pprint.pformat(self.players),
            cities=pprint.pformat({k:v for k,v in self.cities.items() if v.red or v.blue or v.black or v.yellow}),
            diseases=pprint.pformat(self.diseases.values()),
            infection_rate=self.infection_rate(),
            player_discard_pile=pprint.pformat(self.player_discard_pile))

class Runner:
    def __init__(self, players_count=4, difficulty_level=5):
        self.game = build_game(players_count, difficulty_level)
        pprint.pprint(self.game)
    def run(self):
        try:
            while True:
                for player in self.game.players:
                    self.take_turn(player)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            pprint.pprint(self.game)
            print e

    def take_turn(self, player):
        print 'take_turn', player, self.game.cities[player.location]
        actions = 4
        while actions:
            self.update_medic_treat_disease()
            action = self.choose_action(player)
            action()
            actions -= 1
        draw_cards(self.game, player)
        if self.game.next_infector_quiet:
            self.game.next_infector_quiet = False
        else:
            infect(self.game, self.game.infection_rate())

    def update_medic_treat_disease(self):
        # this does not cost an action and can happen at any time
        medics = [player for player in self.game.players if player.role == MEDIC]
        for medic in medics:
            cured_diseases = [disease for disease in self.game.diseases.values() if disease.cured]
            if cured_diseases:
                city = self.game.cities[player.location]
                treatable_colors = [disease.color for disease in cured_diseases if getattr(city, disease.color) > 0]
                for color in treatable_colors:
                    treat_disease(self.game, player, color)

    def available_actions(self, player):
        actions = []
        def make_drive(city): return lambda: drive(player, city)
        actions.extend([make_drive(city) for city in ADJACENT_CITIES[player.location]])
        def make_direct_flight(city): return lambda: direct_flight(self.game, player, city)
        actions.extend([make_direct_flight(city) for city in player.cards if city not in SPECIAL_EVENTS and city != player.location])
        if player.location in player.cards:
            def make_charter_flight(city): return lambda: charter_flight(self.game, player, city)
            actions.extend([make_charter_flight(city) for city in INFECTION_CARDS.keys() if city != player.location])
        if player.location in self.game.research_stations:
            def make_shuttle_flight(city): return lambda: shuttle_flight(self.game, player, city)
            actions.extend([make_shuttle_flight(city) for city in self.game.research_stations if city != player.location])
            
            needed_to_cure = 5
            if player.role == SCIENTIST:
                needed_to_cure = 4
            color_count = Counter([INFECTION_CARDS[city] for city in player.cards if city not in SPECIAL_EVENTS])
            curable_colors = [k for k,v in color_count.iteritems() if v >= needed_to_cure]
            if curable_colors:
                color = curable_colors[0]
                cities = [city for city in player.cards if city not in SPECIAL_EVENTS and INFECTION_CARDS[city] == color][:needed_to_cure]
                actions.append(lambda: discover_cure(self.game, player, cities))
                
        if (player.role == OPERATIONS_EXPERT or player.location in player.cards) and player.location not in self.game.research_stations:
            def make_build_research_station(city): return lambda: build_research_station(self.game, player, city)
            if len(self.game.research_stations) < MAX_RESEARCH_STATIONS:
                actions.append(make_build_research_station(None))
            else:
                # need to designate a station to transfer to new location
                actions.extend([make_build_research_station(city) for city in self.game.research_stations])

        if player.role == DISPATCHER:
            def make_dispatcher_drive(other_player, city): return lambda: dispatcher_drive(player, other_player, city)
            def make_dispatcher_direct_flight(other_player, city): return lambda: dispatcher_direct_flight(self.game, player, other_player, city)
            def make_dispatcher_charter_flight(other_player, city): return lambda: dispatcher_charter_flight(self.game, player, other_player, city)
            def make_dispatcher_shuttle_flight(other_player, city): return lambda: dispatcher_shuttle_flight(self.game, player, other_player, city)
            other_players = [other_player for other_player in self.game.players if other_player != player]
            for other_player in other_players:
                actions.extend([make_dispatcher_drive(other_player, city) for city in ADJACENT_CITIES[other_player.location]])
                actions.extend([make_dispatcher_direct_flight(other_player, city) for city in player.cards if city not in SPECIAL_EVENTS and city != other_player.location])
                if other_player.location in player.cards:
                    actions.extend([make_dispatcher_charter_flight(other_player, city) for city in INFECTION_CARDS.keys() if city != other_player.location])
                if other_player.location in self.game.research_stations:
                    actions.extend([make_dispatcher_shuttle_flight(other_player, city) for city in self.game.research_stations if city != other_player.location])
        
        def make_treat_disease(color): return lambda:treat_disease(self.game, player, color)
        location_city = self.game.cities[player.location]
        actions.extend([make_treat_disease(color) for color in DISEASE_COLORS if getattr(location_city, color) > 0])

        colocated_players = [other_player for other_player in self.game.players if other_player.location == player.location and player != other_player]
        print 'colocated_players', colocated_players
        if colocated_players:
            def make_share_knowledge(from_player, to_player, card): return lambda:share_knowledge(from_player, to_player, card)
            if player.role == RESEARCHER:
                print 'player.role == RESEARCHER'
                for other_player in colocated_players:
                    for card in player.cards:
                        print player.role, other_player.role, card
                        actions.append(make_share_knowledge(player, other_player, card)) 
            elif player.location in player.cards:
                print 'player.location in player.cards'
                for other_player in colocated_players:
                    print player.role, other_player.role, player.location
                    actions.append(make_share_knowledge(player, other_player, player.location))
            for other_player in colocated_players:
                if other_player.role == RESEARCHER:
                    print 'other_player.role == RESEARCHER'
                    for card in other_player.cards:
                        print other_player.role, player.role, card
                        actions.append(make_share_knowledge(other_player, player, card))
                elif other_player.location in other_player.cards:
                    print 'other_player.location in other_player.cards'
                    print other_player.role, player.role, other_player.location
                    actions.append(make_share_knowledge(other_player, player, other_player.location))
        return actions
    
    def choose_action(self, player):
        return random.choice(self.available_actions(player))

class DefeatException(Exception):
    pass

class VictoryException(Exception):
    pass

if __name__ == '__main__':
    runner = Runner()
    runner.run()

