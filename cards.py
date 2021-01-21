from dataclasses import dataclass, field
from typing import List

import requests


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

    def init_objects_with_names(self, name_one: str, name_two: str):
        self.players.append(Player(name=name_one))
        self.players.append(Player(name=name_two))
        self.piles.append(Pile())
        self.piles.append(Pile())

    def load_data_new_game(self, name_one: str, name_two: str):
        self.init_objects_with_names(name_one=name_one, name_two=name_two)
        new_deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle")
        self.deck_id = new_deck.json()['deck_id']
        response = requests.get('https://deckofcardsapi.com/api/deck/' + self.deck_id + '/draw/?count=52')
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
        for i in range(40, 45):
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

    def can_be_placed(self, player_id: int, pile_id: int, card_id: int) -> bool:
        if (self.PREVIOUS_CARD.get(str(self.players[player_id].hand[card_id].value)) == self.piles[
            pile_id].visible.value or
                self.NEXT_CARD.get(str(self.players[player_id].hand[card_id].value)) == self.piles[
                    pile_id].visible.value):
            return True
        return False

    def add_missing_cards(self, player_id: int):
        print(len(self.players[player_id].hand), len(self.players[player_id].hidden))
        for card in self.players[player_id].hand:
            if len(self.players[player_id].hidden) == 0:
                break
            if card is None:
                self.add_card(player_id, self.players[player_id].hand.index(card))
        print(len(self.players[player_id].hand), len(self.players[player_id].hidden))
        for card in self.players[player_id].hand:
            print(card)

    def add_card(self, player_id: int, list_index: int):
        self.players[player_id].hand.pop(list_index)
        self.players[player_id].hand.insert(list_index, self.players[player_id].hidden[0])
        self.players[player_id].hidden.pop(0)

    def has_won(self, player_id: int) -> bool:
        if len(self.players[player_id].hand) == 0 and len(self.players[player_id].hidden) == 0:
            return True
        return False

    def turn_card_on_piles(self):
        if self.can_cards_be_turned_on_piles():
            for i in range(0, 2):
                self.piles[i].hidden.append(self.piles[i].visible)
                self.piles[i].visible = self.piles[i].hidden[0]
                self.piles[i].hidden.pop(0)

    def can_cards_be_turned_on_piles(self) -> bool:
        for i in range(0, 5):
            if (self.can_be_placed(player_id=0, pile_id=0, card_id=i) or
                    self.can_be_placed(player_id=0, pile_id=1, card_id=i) or
                    self.can_be_placed(player_id=1, pile_id=0, card_id=i) or
                    self.can_be_placed(player_id=1, pile_id=1, card_id=i)):
                return False
        return True

    def save_deck_to_api(self):
        for i in range(0, 2):
            for card in self.players[i].hidden:
                if card is not None:
                    requests.get(
                        'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(i) + '_hidden/add/?cards=' +
                        card.code)

            for card in self.players[i].hand:
                if card is not None:
                    requests.get(
                        'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(i) + '_hand/add/?cards=' +
                        card.code)

            for card in self.piles[i].hidden:
                if card is not None:
                    requests.get(
                        'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(i) + '_hidden/add/?cards=' +
                        card.code)

            if self.piles[i].visible.code is not None:
                requests.get(
                    'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(i) + '_visible/add/?cards=' +
                    self.piles[i].visible.code)

    def load_deck_from_api(self, name_one: str, name_two: str, deck_id: str):
        self.init_objects_with_names(name_one=name_one, name_two=name_two)
        self.deck_id = deck_id
        for i in range(0, 2):
            resp = requests.get('https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(i) + '_hand/list/')
            resp = resp.json().get('piles').get('player_' + str(i) + '_hand').get('cards')
            for card in resp:
                print(card['code'])
                self.players[i].hand.append(Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))

            resp = requests.get('https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(i) + '_hidden/list/')
            resp = resp.json().get('piles').get('player_' + str(i) + '_hidden').get('cards')
            for card in resp:
                self.players[i].hidden.append(Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))

            resp = requests.get('https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(i) + '_hidden/list/')
            resp = resp.json().get('piles').get('pile_' + str(i) + '_hidden').get('cards')
            for card in resp:
                self.piles[i].hidden.append(Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))

            resp = requests.get('https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(i) + '_visible/list/')
            resp = resp.json().get('piles').get('pile_' + str(i) + '_visible').get('cards')
            for card in resp:
                self.piles[i].visible = Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code'])

    def print_lists(self):
        print(self.deck_id)
        for i in range(0, 2):
            print(i, 'hand')
            for card in self.players[i].hand:
                print(card)
            print(i, 'hidden player')
            for card in self.players[i].hidden:
                print(card)
            print(i, 'visible')
            print(self.piles[i].visible)
            print(i, 'hidden pile')
            for card in self.piles[i].hidden:
                print(card)

