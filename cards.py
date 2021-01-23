import json
import os
from dataclasses import dataclass, field
from typing import List

import requests
from pip._internal.utils.misc import consume


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

    def __post_init__(self):
        self.players.append(Player(name='player1'))
        self.players.append(Player(name='player2'))
        self.piles.append(Pile())
        self.piles.append(Pile())
        for i in range(0, 2):
            self.piles[i].visible = None

    def update_names(self, name_one: str, name_two: str):
        self.players[0].name = name_one
        self.players[1].name = name_two

    def load_data_new_game(self, name_one: str, name_two: str):
        self.update_names(name_one=name_one, name_two=name_two)
        new_deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle")
        self.deck_id = new_deck.json()['deck_id']
        response = requests.get('https://deckofcardsapi.com/api/deck/' + self.deck_id + '/draw/?count=52')
        response = response.json()
        cards = list()
        for el in response.get('cards'):
            cards.append(el)
        for i in range(0, 15):
            for j in range(0, 2):
                self.players[j].hidden \
                    .append(Card(image=cards[i + (j * 15)]['image'], value=cards[i + (j * 15)]['value'],
                                 suit=cards[i + (j * 15)]['suit'],
                                 code=cards[i + (j * 15)]['code']))
        for i in range(30, 35):
            for j in range(0, 2):
                self.players[j].hand \
                    .append(
                    Card(image=cards[i + j * 5]['image'], value=cards[i + j * 5]['value'],
                         suit=cards[i + j * 5]['suit'],
                         code=cards[i + j * 5]['code']))
        for i in range(40, 45):
            for j in range(0, 2):
                self.piles[j].hidden \
                    .append(
                    Card(image=cards[i + j * 5]['image'], value=cards[i + j * 5]['value'],
                         suit=cards[i + j * 5]['suit'],
                         code=cards[i + j * 5]['code']))
        self.piles[0].visible = Card(image=cards[50]['image'], value=cards[50]['value'], suit=cards[50]['suit'],
                                     code=cards[50]['code'])
        self.piles[1].visible = Card(image=cards[51]['image'], value=cards[51]['value'], suit=cards[51]['suit'],
                                     code=cards[51]['code'])
        self.load_images()

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
                        'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(
                            i) + '_hidden/add/?cards=' +
                        card.code)

            for card in self.players[i].hand:
                if card is not None:
                    requests.get(
                        'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(
                            i) + '_hand/add/?cards=' +
                        card.code)

            for card in self.piles[i].hidden:
                if card is not None:
                    requests.get(
                        'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(
                            i) + '_hidden/add/?cards=' +
                        card.code)

            if self.piles[i].visible.code is not None:
                requests.get(
                    'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(
                        i) + '_visible/add/?cards=' +
                    self.piles[i].visible.code)

    def load_deck_from_api(self, name_one: str, name_two: str, deck_id: str):
        self.update_names(name_one=name_one, name_two=name_two)
        self.deck_id = deck_id
        for i in range(0, 2):
            resp = requests.get(
                'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(i) + '_hand/list/')
            resp = resp.json().get('piles').get('player_' + str(i) + '_hand').get('cards')
            for card in resp:
                print(card['code'])
                self.players[i].hand.append(
                    Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))

            resp = requests.get(
                'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/player_' + str(i) + '_hidden/list/')
            resp = resp.json().get('piles').get('player_' + str(i) + '_hidden').get('cards')
            for card in resp:
                self.players[i].hidden.append(
                    Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))

            resp = requests.get(
                'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(i) + '_hidden/list/')
            resp = resp.json().get('piles').get('pile_' + str(i) + '_hidden').get('cards')
            for card in resp:
                self.piles[i].hidden.append(
                    Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))

            resp = requests.get(
                'https://deckofcardsapi.com/api/deck/' + self.deck_id + '/pile/pile_' + str(i) + '_visible/list/')
            resp = resp.json().get('piles').get('pile_' + str(i) + '_visible').get('cards')
            for card in resp:
                self.piles[i].visible = Card(image=card['image'], value=card['value'], suit=card['suit'],
                                             code=card['code'])
        self.load_images()

    def print_lists(self):
        print(self.deck_id)
        for i in range(0, 2):
            print(i, 'hand')
            consume(print(card) for card in self.players[i].hand)
            print(i, 'hidden player')
            consume(print(card) for card in self.players[i].hidden)
            print(i, 'visible')
            if self.piles[i].visible is not None:
                print(self.piles[i].visible)
            print(i, 'hidden pile')
            consume(print(card) for card in self.piles[i].hidden)

    def save_id_to_file(self):
        path = 'resources/saves'
        if not os.path.exists(path):
            os.makedirs(path)
        file = open(path + '/deck_id.txt', 'w')
        file.write(self.deck_id)

    def open_id_from_file(self):
        path = 'resources/card_images/deck_id.txt'
        if os.path.exists(path):
            with open('deck_id.txt', 'r') as file:
                self.deck_id = file.read()
        else:
            print('there is no save')

    def save_deck_to_json(self):
        path = 'resources/saves'
        if not os.path.exists(path):
            os.makedirs(path)
        json_str = json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=5)
        with open(path + '/save.json', 'w') as file:
            file.write(json_str)

    def open_deck_from_json(self):
        path = 'resources/saves'
        if os.path.exists(path):
            with open('save.json', 'r') as file:
                data = json.load(file)
                self.deck_id = data['deck_id']
        else:
            print('there is no save')

        i = 0
        print(data.get('players'))
        for el in data['players']:
            for card in el['hand']:
                self.players[i].hand.append(
                    Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))
            for card in el['hidden']:
                self.players[i].hidden.append(
                    Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))
            self.players[i].name = el['name']
            i += 1

        i = 0
        for el in data.get('piles'):
            for card in el['hidden']:
                self.piles[i].hidden.append(
                    Card(image=card['image'], value=card['value'], suit=card['suit'], code=card['code']))
            for card in el['visible']:
                self.piles[i].visible = Card(image=card['image'], value=card['value'],
                                         suit=card['suit'], code=card['code'])
            i += 1
        self.load_images()

    def load_images(self):
        path = 'resources/card_images'
        if not os.path.exists(path):
            os.makedirs(path)
        consume(consume(self.load_image(path, card) for card in self.players[i].hand) for i in range(0, 2))
        consume(consume(self.load_image(path, card) for card in self.players[i].hidden) for i in range(0, 2))
        consume(consume(self.load_image(path, card) for card in self.piles[i].hidden) for i in range(0, 2))
        consume(self.load_image(path, self.piles[i].visible) for i in range(0, 2))

    def load_image(self, path: str, card: Card):
        path = 'resources/card_images'
        if not os.path.exists(path + '/' + card.code + '.png'):
            response = requests.get(card.image)
            with open(path + '/' + card.code + '.png', 'wb') as file:
                file.write(response.content)
