import sys
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
    CARD_WIDTH_PILES = 200

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

    def main_menu(self):
        run = True
        while run:
            self.screen.fill((255, 0, 255))
            background = pygame.image.load('resources/board_background.png')
            self.screen.blit(background, (0, 0))

            self.draw_text_menu('main menu', self.BLACK, 100, 'head')

            mx, my = pygame.mouse.get_pos()

            start_button = pygame.Rect(0, 0, self.MENU_BUTTON_WIDTH, self.MENU_BUTTON_HEIGHT)
            start_button.center = (self.WINDOW_WIDTH / 2, 300)
            if start_button.collidepoint((mx, my)):
                if self.click:
                    self.game()
            pygame.draw.rect(self.screen, self.WHITE, start_button)
            self.draw_text_menu('NEW GAME', self.BLACK, 300)

            load_game_from_api_button = pygame.Rect(0, 0, self.MENU_BUTTON_WIDTH, self.MENU_BUTTON_HEIGHT)
            load_game_from_api_button.center = (self.WINDOW_WIDTH / 2, 500)
            if load_game_from_api_button.collidepoint((mx, my)):
                if self.click:
                    self.game('api save')
            pygame.draw.rect(self.screen, self.WHITE, load_game_from_api_button)
            self.draw_text_menu('LOAD GAME FROM API', self.BLACK, 500)

            load_game_from_save_button = pygame.Rect(0, 0, self.MENU_BUTTON_WIDTH, self.MENU_BUTTON_HEIGHT)
            load_game_from_save_button.center = (self.WINDOW_WIDTH / 2, 700)
            if load_game_from_save_button.collidepoint((mx, my)):
                if self.click:
                    self.game('json save')
            pygame.draw.rect(self.screen, self.WHITE, load_game_from_save_button)
            self.draw_text_menu('LOAD GAME FROM SAVE', self.BLACK, 700)

            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
            pygame.display.update()

    def game(self, start_type: str = 'new game'):
        self.screen.fill((0, 0, 0, 0))
        if start_type == 'new game':
            self.deck.load_data_new_game(name_one='X', name_two='D')
        elif start_type == 'json save':
            self.deck.open_deck_from_json()
        elif start_type == 'api save':
            self.deck.open_id_from_file()
            id = self.deck.deck_id
            self.deck.load_deck_from_api(name_one='x', name_two='d', deck_id=id)
        self.chosen_card = [-1 for i in range(0, 2)]
        run = True
        while run:
            self.draw_text_menu('temp' + start_type, self.BLACK, 200)
            background = pygame.image.load('resources/board_background.png')
            self.screen.blit(background, (0, 0))
            self.draw_cards()
            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True

            pygame.display.update()

    def draw_cards(self):
        mx, my = pygame.mouse.get_pos()

        for i in range(0, 2):
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
                        pass
                    self.screen.blit(card, card_rect)
                width += 150
            width += 50
            if len(self.deck.players[i].hidden) > 0:
                card = pygame.image.load('resources/card_back.png')
                card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                self.screen.blit(card, (width, self.CARD_HEIGHT_PLAYERS[i]))
            if i == 0:
                width = self.CARD_WIDTH_PILES
                card = pygame.image.load('resources/card_back.png')
                card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                self.screen.blit(card, (width, self.CARD_HEIGHT_PILES))
                width += 200
                card = pygame.image.load('resources/card_images/' + self.deck.piles[i].visible.code + '.png')
                card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                self.screen.blit(card, (width, self.CARD_HEIGHT_PILES))
            else:
                width = 1000 - self.CARD_WIDTH_PILES
                card = pygame.image.load('resources/card_back.png')
                card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                self.screen.blit(card, (width, self.CARD_HEIGHT_PILES))
                width -= 200
                card = pygame.image.load('resources/card_images/' + self.deck.piles[i].visible.code + '.png')
                card = pygame.transform.scale(card, (self.CARD_WIDTH, self.CARD_HEIGHT))
                self.screen.blit(card, (width, self.CARD_HEIGHT_PILES))

    def draw_text_menu(self, text, color, height: int, type: str = 'button'):
        if type == 'head':
            text_obj = self.MENU_HEADLINE_FONT.render(text, True, color)
        else:
            text_obj = self.MENU_BUTTON_FONT.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (self.WINDOW_WIDTH / 2, height)
        self.screen.blit(text_obj, text_rect)


g = Game()
g.run()
