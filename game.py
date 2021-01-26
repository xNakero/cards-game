import sys
import threading
from dataclasses import dataclass, field
from typing import List

import pygame
from pip._internal.utils.misc import consume
from pygame.locals import *

import cards


@dataclass
class Game:
    click = False
    screen: pygame.display = field(init=False)
    deck = cards.Deck()
    # chosen card for players 0 or 1, 0 - 4 are cards, else is nothing chosen
    chosen_card: List[int] = field(default_factory=list)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (120, 114, 118)
    CARD_WIDTH = 113
    CARD_HEIGHT = 157
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MENU_BUTTON_WIDTH = 500
    MENU_BUTTON_HEIGHT = 120
    MENU_BUTTON_FONT: pygame.font = field(init=False)
    MENU_HEADLINE_FONT: pygame.font = field(init=False)
    CARD_HEIGHT_PLAYERS = [600, 43]
    CARD_STARTING_WIDTH_PLAYERS = 100
    CARD_HEIGHT_PILES = 321
    CARD_WIDTH_PILES = 175

    def __post_init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.screen.fill((255, 255, 255))
        pygame.display.set_caption('Speed card game')
        self.MENU_HEADLINE_FONT = pygame.font.SysFont('comicsandms', 100)
        self.MENU_BUTTON_FONT = pygame.font.SysFont('comicsandms', 50)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEMOTION:
                    self.main_menu()
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def menu_background(self):
        self.screen.fill((255, 0, 255))
        background = pygame.image.load('resources/board_background.png')
        self.screen.blit(background, (0, 0))

    def main_menu(self):
        run = True
        while run:
            self.menu_background()
            self.draw_text('main menu', self.BLACK, 100, 'head')

            mx, my = pygame.mouse.get_pos()
            load_types = ['new game', 'api save', 'json save']
            texts = ['NEW GAME', 'LOAD GAME FROM API', 'LOAD GAME FROM SAVE']
            heights = [300, 500, 700]
            consume(self.menu_button(mx=mx, my=my, height=heights[i], load_type=load_types[i], text=texts[i])
                    for i in range(0, 3))

            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
            pygame.display.update()

    def menu_button(self, mx: int, my: int, height: int, load_type: str, text: str):
        button = pygame.Rect(0, 0, self.MENU_BUTTON_WIDTH, self.MENU_BUTTON_HEIGHT)
        button.center = (self.WINDOW_WIDTH / 2, height)
        if button.collidepoint((mx, my)):
            if self.click:
                if load_type == 'json save' and self.deck.json_save_exists() or \
                        load_type == 'api save' and self.deck.deck_id_save_exists() or \
                        load_type == 'new game':
                    self.load(load_type)
        if (load_type == 'json save' and self.deck.json_save_exists()) or (
                load_type == 'api save' and self.deck.deck_id_save_exists()) or load_type == 'new game':
            pygame.draw.rect(self.screen, self.WHITE, button)
        else:
            pygame.draw.rect(self.screen, self.GREY, button)
        self.draw_text(text, self.BLACK, height)

    def load(self, load_type: str = 'new game'):
        self.menu_background()
        self.draw_text('LOADING', self.WHITE, 400)
        pygame.display.update()
        self.game(load_type)

    def game(self, start_type: str = 'new game'):
        self.screen.fill((0, 0, 0))
        self.deck = cards.Deck()
        if start_type == 'new game':
            self.deck.load_data_new_game(name_one='player 1', name_two='player 2')
        elif start_type == 'json save':
            self.deck.open_deck_from_json()
        elif start_type == 'api save':
            self.deck.open_id_from_file()
            deck_id = self.deck.deck_id
            self.deck.load_deck_from_api(name_one='player 1', name_two='player 2', deck_id=deck_id)

        self.chosen_card = [-1 for i in range(0, 2)]

        run = True
        while run:
            background = pygame.image.load('resources/board_background.png')
            self.screen.blit(background, (0, 0))
            self.draw_cards()
            self.draw_text(text='I - save to json', color=self.WHITE, height=350, width=1000)
            self.draw_text(text='O - save to api', color=self.WHITE, height=450, width=1000)
            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                elif event.type == KEYDOWN:
                    if event.key == K_1:
                        if self.chosen_card[1] == 0:
                            self.chosen_card[1] = -1
                        else:
                            self.chosen_card[1] = 0
                    elif event.key == K_2:
                        if self.chosen_card[1] == 1:
                            self.chosen_card[1] = -1
                        else:
                            self.chosen_card[1] = 1
                    elif event.key == K_3:
                        if self.chosen_card[1] == 2:
                            self.chosen_card[1] = -1
                        else:
                            self.chosen_card[1] = 2
                    elif event.key == K_4:
                        if self.chosen_card[1] == 3:
                            self.chosen_card[1] = -1
                        else:
                            self.chosen_card[1] = 3
                    elif event.key == K_5:
                        if self.chosen_card[1] == 4:
                            self.chosen_card[1] = -1
                        else:
                            self.chosen_card[1] = 4
                    elif event.key == K_q:
                        if self.chosen_card[1] in range(0, 5):
                            self.deck.play_card(player_id=1, pile_id=0, card_id=self.chosen_card[1])
                            if self.deck.has_won(player_id=1):
                                print('won game')
                                self.end_game(self.deck.players[1].name)
                        self.chosen_card[1] = -1
                    elif event.key == K_w:
                        if self.chosen_card[1] in range(0, 5):
                            self.deck.play_card(player_id=1, pile_id=1, card_id=self.chosen_card[1])
                            if self.deck.has_won(player_id=1):
                                print('won game')
                                self.end_game(self.deck.players[1].name)
                                run = False
                        self.chosen_card[1] = -1
                    elif event.key == K_r:
                        self.deck.add_missing_cards(player_id=1)
                    elif event.key == K_SPACE:
                        self.deck.turn_cards_on_piles()
                    elif event.key == K_i:
                        self.save()
                    elif event.key == K_o:
                        self.save('api')
                    elif event.key == K_ESCAPE:
                        run = False
            pygame.display.update()

    def draw_cards(self):
        mx, my = pygame.mouse.get_pos()

        for i in range(0, 2):
            # hand
            width = self.CARD_STARTING_WIDTH_PLAYERS
            for card in self.deck.players[i].hand:
                if card is not None:
                    index = self.deck.players[i].hand.index(card)
                    card = pygame.image.load('resources/card_images/' + card.code + '.png')
                    card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                    card_rect = card.get_rect()
                    card_rect.left = width
                    card_rect.top = self.CARD_HEIGHT_PLAYERS[i]
                    if i == 0:
                        if card_rect.collidepoint(mx, my):
                            if self.click:
                                if self.chosen_card[i] == index:
                                    self.chosen_card[i] = -1
                                else:
                                    self.chosen_card[i] = index
                                print(self.chosen_card[i])
                        if self.chosen_card[i] == index:
                            card_rect.y -= 20
                    else:
                        if self.chosen_card[i] == index:
                            card_rect.y += 20
                    self.screen.blit(card, card_rect)
                width += 150
            width += 50
            # hidden
            if len(self.deck.players[i].hidden) > 0:
                card = pygame.image.load('resources/card_back.png')
                card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                card_rect = card.get_rect()
                card_rect.left = width
                card_rect.top = self.CARD_HEIGHT_PLAYERS[i]
                if i == 0 and card_rect.collidepoint(mx, my) and self.click:
                    self.deck.add_missing_cards(player_id=0)
                self.screen.blit(card, card_rect)
        # piles
        # pile left hidden
        width_piles = self.CARD_WIDTH_PILES
        card = pygame.image.load('resources/card_back.png')
        card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
        card_rect = card.get_rect()
        card_rect.left = width_piles
        card_rect.top = self.CARD_HEIGHT_PILES
        if card_rect.collidepoint(mx, my) and self.click:
            self.deck.turn_cards_on_piles()
        self.screen.blit(card, card_rect)
        width_piles += 150
        # piles visible
        for i in range(0, 2):
            card = pygame.image.load('resources/card_images/' + self.deck.piles[i].visible.code + '.png')
            card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
            card_rect = card.get_rect()
            card_rect.left = width_piles
            card_rect.top = self.CARD_HEIGHT_PILES
            if card_rect.collidepoint(mx, my) and self.click and self.chosen_card[0] in range(0, 5):
                self.deck.play_card(player_id=0, pile_id=i, card_id=self.chosen_card[0])
                if self.deck.has_won(player_id=0):
                    print('won game')
                    self.end_game(self.deck.players[0].name)
                self.chosen_card[0] = -1
            self.screen.blit(card, card_rect)
            width_piles += 150
        # right pile hidden
        card = pygame.image.load('resources/card_back.png')
        card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
        card_rect = card.get_rect()
        card_rect.left = width_piles
        card_rect.top = self.CARD_HEIGHT_PILES
        if card_rect.collidepoint(mx, my) and self.click:
            self.deck.turn_cards_on_piles()
        self.screen.blit(card, card_rect)

    def save(self, save_type: str = 'json'):
        self.screen.fill(self.WHITE)
        run = threading.Event()
        threading.Thread(target=self.save_thread, args=[save_type, run]).start()
        while not run.is_set():
            self.draw_text(text='SAVING', color=self.BLACK, height=400, type='else')
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def save_thread(self, save_type: str, event):
        if save_type == 'api':
            self.deck.save_deck_to_api()
            self.deck.save_id_to_file()
        else:
            self.deck.save_deck_to_json()
        event.set()

    def end_game(self, name: str):
        self.screen.fill((0, 0, 0))
        background = pygame.image.load('resources/board_background.png')
        self.screen.blit(background, (0, 0))
        run = True
        while run:
            self.draw_text(text='winner is ' + name, color=self.WHITE, height=400, type='else')
            self.draw_text(text='press any key to return to menu', color=self.WHITE, height=600)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.main_menu()
            pygame.display.update()

    def draw_text(self, text, color, height: int, type: str = 'button', width: int = None):
        if width is None:
            width = self.WINDOW_WIDTH / 2
        if type == 'head':
            text_obj = self.MENU_HEADLINE_FONT.render(text, True, color)
        else:
            text_obj = self.MENU_BUTTON_FONT.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (width, height)
        self.screen.blit(text_obj, text_rect)


g = Game()
g.main_menu()
