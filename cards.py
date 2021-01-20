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


@dataclass()
class GameData:
    deck_id: str = field(init=False)
    left_pile_visible: Card = field(init=False)
    right_pile_visible: Card = field(init=False)
    player_one_name: str
    player_two_name: str
    player_one_hand: List[Card] = field(default_factory=list)
    player_one_visible: List[Card] = field(default_factory=list)
    player_two_hand: List[Card] = field(default_factory=list)
    player_two_visible: List[Card] = field(default_factory=list)
    left_pile: List[Card] = field(default_factory=list)
    right_pile: List[Card] = field(default_factory=list)

    def load_data(self):
        new_deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle")
        deck_id = new_deck.json()['deck_id']
        response = requests.get('https://deckofcardsapi.com/api/deck/' + deck_id + '/draw/?count=52')
        response = response.json()
        codes = list()
        for el in response.get('cards'):
            codes.append(el)
            print(el)
        print(len(codes))
        for i in range(0, 15):
            self.player_one_hand \
                .append(
                Card(image=codes[i]['image'], value=codes[i]['value'], suit=codes[i]['suit'], code=codes[i]['code']))
            self.player_two_hand \
                .append(Card(image=codes[i + 15]['image'], value=codes[i + 15]['value'], suit=codes[i + 15]['suit'],
                             code=codes[i + 15]['code']))
        for i in range(30, 35):
            self.player_one_visible \
                .append(
                Card(image=codes[i]['image'], value=codes[i]['value'], suit=codes[i]['suit'], code=codes[i]['code']))
            self.player_two_visible \
                .append(Card(image=codes[i + 5]['image'], value=codes[i + 5]['value'], suit=codes[i + 5]['suit'],
                             code=codes[i + 5]['code']))
        for i in range(36, 40):
            self.left_pile \
                .append(
                Card(image=codes[i]['image'], value=codes[i]['value'], suit=codes[i]['suit'], code=codes[i]['code']))
            self.right_pile \
                .append(Card(image=codes[i + 5]['image'], value=codes[i + 5]['value'], suit=codes[i + 5]['suit'],
                             code=codes[i + 5]['code']))
        self.left_pile_visible = Card(image=codes[50]['image'], value=codes[50]['value'], suit=codes[50]['suit'],
                                      code=codes[50]['code'])
        self.right_pile_visible = Card(image=codes[51]['image'], value=codes[51]['value'], suit=codes[51]['suit'],
                                       code=codes[51]['code'])


