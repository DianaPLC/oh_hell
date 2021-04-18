# Oh Hell
A trick-based card game
## To Play
Run `python3 game_tester.py` in the command line and follow the prompts. You will play as 'User' against 3 bots. User will lead the round.
> Note: Currently, for testing purposes, any input other than "y" or "Y" on a "Y/N" prompt will cause the program to exit. Other prompts have validation that will handle errors more gracefully.
## Project Status
Currently the project contains the fundamental units of the back-end logic of the game, with a file that runs the first round of a 4-person game as a CLI text-prompt game.
### To Do
- Add a card-pick stage to determine first lead.
- Add logic to prevent user-entered disallowed bid.
- Expand logic to run a game from start to finish through multiple rounds.
- Create visual front-end.
  - Ideally include cards-up option for easier debugging of bot logic.
- Create user options, incl. player naming and card ordering
- Create online app with multi-user login
- Create multiplayer version for pvp online play
## Rules
The term "Oh Hell" seems to apply to a wide variety of slightly different games. The version here is based on the Trinity gameplay, which follows the [Common Rules](https://en.wikipedia.org/wiki/Oh_Hell#Common_rules) with the following addenda:
- First player is selected by a random draw of cards; Higher card values win, with the tie going to the higher suit (in bridge rules suit order)
- In the first round, cards are dealt out until all players have the same number of cards *and* the number of cards remaining in the deck is <= to the number of players.
  - For instance, in a 5-person game, each player receives 10 cards, with 2 remaining in the deck; in a 4-person game, each player receives 12 cards, with 4 remaining in the deck.
  - In a 3-person game, players may choose to cap the hand size at 12 rather than having to manage a 17-card hand.
  - After the first round, the hand size decreases by 1 per round until in the final round each player receives 1 card.
  - The total tricks bid **cannot** add up to the hand size for the round (ie. it's not allowed to bid such that everyone could get their bid). This means that the final person bidding cannot say a value that would result in the sum of bids being equal to the hand size.
