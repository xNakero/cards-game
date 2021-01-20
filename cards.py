from dataclasses import dataclass, field
from typing import List

import requests

"""
    def new_game(self):
        new_deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle")
        deck_id = new_deck.json()['deck_id']
        response = requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/draw/?count=52')
        response = response.json()
        codes = list()
        for el in response.get('cards'):
            codes.append(el['code'])
            print(el['code'])
        print(len(codes))
        for i in range(0, 15):
            player_one_hand.append()
            
            requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/player1_hand/add/?cards=' + codes[i])
            requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/player2_hand/add/?cards=' + codes[i + 10])
        for i in range(30, 35):
            requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/player1/add/?cards=' + codes[i])
            requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/player2/add/?cards=' + codes[i+5])
        for i in range(36, 40):
            requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/left_pile/add/?cards=' + codes[i])
            requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/right_pile/add/?cards=' + codes[i + 10])
        requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/left_pile_visible/add/?cards=' + codes[50])
        requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/pile/right_pile_visible/add/?cards=' + codes[51])
"""


@dataclass
class Card:
    image: str
    value: str
    suit: str
    code: str


@dataclass
class Player:
    name: str
    hand: List[Card] = field(default_factory=list)
    hidden: List[Card] = field(default_factory=list)


@dataclass
class Pile:
    visible: Card = field(init=False)
    hidden: List[Card] = field(default_factory=list)


@dataclass()
class Deck:
    PREVIOUS_CARD = {'2': 'ACE', '3': '2', '4': '3', '5': '4', '6': '5', '7': '6', '8': '7', '9': '8', '0': '9',
                     'JACK': '0',
                     'QUEEN': 'JACK', 'KING': 'QUEEN', 'ACE': 'KING'}
    NEXT_CARD = {'2': '3', '3': '4', '4': '5', '5': '6', '6': '7', '7': '8', '8': '9', '9': '0', '0': 'JACK',
                 'JACK': 'QUEEN', 'QUEEN': 'KING', 'KING': 'ACE', 'ACE': '2'}
    deck_id: str = field(init=False)
    players: List[Player] = field(default_factory=list)
    piles: List[Pile] = field(default_factory=list)

    def load_data_new_game(self, name_one: str, name_two: str):
        self.players.append(Player(name=name_one))
        self.players.append(Player(name=name_two))
        self.piles.append(Pile())
        self.piles.append(Pile())
        new_deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle")
        deck_id = new_deck.json()['deck_id']
        response = requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/draw/?count=52')
        response = response.json()
        codes = list()
        for el in response.get('cards'):
            codes.append(el)
        for i in range(0, 15):
            for j in range(0, 2):
                self.players[j].hidden \
                    .append(Card(image=codes[i + (j * 15)]['image'], value=codes[i + (j * 15)]['value'],
                                 suit=codes[i + (j * 15)]['suit'],
                                 code=codes[i + (j * 15)]['code']))
        for i in range(30, 35):
            for j in range(0, 2):
                self.players[j].hand \
                    .append(
                    Card(image=codes[i + j * 5]['image'], value=codes[i + j * 5]['value'],
                         suit=codes[i + j * 5]['suit'],
                         code=codes[i + j * 5]['code']))
        for i in range(36, 40):
            for j in range(0, 2):
                self.piles[j].hidden \
                    .append(
                    Card(image=codes[i + j * 5]['image'], value=codes[i + j * 5]['value'],
                         suit=codes[i + j * 5]['suit'],
                         code=codes[i + j * 5]['code']))
        self.piles[0].visible = Card(image=codes[50]['image'], value=codes[50]['value'], suit=codes[50]['suit'],
                                     code=codes[50]['code'])
        self.piles[1].visible = Card(image=codes[51]['image'], value=codes[51]['value'], suit=codes[51]['suit'],
                                     code=codes[51]['code'])

    def play_card(self, player_id: int, pile_id: int, card_id: int):
        if self.can_be_placed(player_id, pile_id, card_id):
            self.piles[pile_id].hidden.append(self.piles[pile_id].visible)
            self.piles[pile_id].visible = self.players[player_id].hand[card_id]
            self.players[player_id].hand[card_id] = None
            for i in range(0, 5):
                print(self.players[player_id].hand[i])


    def can_be_placed(self, player_id: int, pile_id, card_id):
        print(self.players[player_id].hand[card_id].value)
        print(self.piles[pile_id].visible.value)
        if (self.PREVIOUS_CARD.get(str(self.players[player_id].hand[card_id].value)) == self.piles[pile_id].visible.value or
                self.NEXT_CARD.get(str(self.players[player_id].hand[card_id].value)) == self.piles[pile_id].visible.value):
            return True
        return False

