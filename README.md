# Speed card game

## Rules of the game
Each player is dealt 20 cards, of which 5 form a hand and the rest are dealt face down. The rest of the cards that are 
not given to players are placed in the middle between the players on 2 piles each 6 cards, of which only one is visible 
at the same time. 

The goal of the game is to get rid of all 20 cards that player is given in the beginning by placing them on 1 of 2 
visible cards in the middle. Cards can be placed on visible piles if they are one number above or one number below the 
one on pile. For example if on the left visible pile is a King only a Queen or an Ace can be placed, if there is an Ace 
only a King or a 2 can be placed. Once player places the card he is left with one less card in hand, it is then possible
to add one or more card from face down cards if they are available to refill hand to 5 cards. If none of the players can
add more cards to their hands and they have no available move to make then one of the players can turn cards on both 
piles in the middle until one of players can make a move.

## Controls
The player at the bottom is the mouse user, he does everything by clicking. He can choose one of his cards by clicking 
on it and then click one of piles to place it there. If the move is possible it will be placed. He can refill his hand 
by clicking on a face down card next to his hand. He also can turn cards on pile by clicking on one of the cards face 
down next to the piles.

The player on the top is the keyboard user. His controls are:

**1** - choose first card from the left

**2** - choose second card from the left

**3** - choose third card from the left

**4** - choose fourth card from the left

**5** - choose fifth card from the left

**Q** - place chosen card on left pile

**W** - place chosen card on right pile

**R** - refill the hand

**SPACE** - turn cards on piles

Outside of the game controls there are few other things to do:

**I** - save to local json save

**O** - save to api

**ESC** - return to menu

## Tools used
To implement the game I used pygame library. In order to get cards data I used http://deckofcardsapi.com/ which allowed
me to get cards data, images and to implement saving to the api, so the game can be opened in any place given that the 
deck id is known.
