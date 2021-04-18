import random

class UserError(Exception):
    pass

#Testing:
    #from card_handlers import Deck
    #deck = Deck()
    #deck.shuffle()
    #played_cards = deck.set_trump()
    #player_list = deck.deal(4,12)
    #print(player_list["Player1"])
    #player_list["Player1"].set_bid_values(deck,played_cards,4,player_list)
    #print(player_list["Player1"])

'''
Game Logic to Build:
    Round:
        1. Set Leader (+1 from last leader)
        2. Trick leader = leader
        3. Calculate hand bid values
        4. Set bids in order from leader
            i. First bid = bid value rounded naively
            ii. Middle bids =
                bid value rounded up if (total bid/players who have bid) < (hand size/players);
                bid value rounded down if (total bid/players who have bid) > (hand size/players);
                bid value rounded naively if (total bid/players who have bid) == (hand size/players)
            iii. Last bid =
                bid value rounded up if ([hand size] - [total bid]) == bid value rounded down
                bid value rounded down if ([hand size] - [total bid]) == bid value rounded up
                bid value rounded naively otherwise
        5. Start Trick: trick leader plays card
        6. Play trick: [the below applies in all "play card" circumstances, I think? well enough?]
            if bid value <= (bid-round score) and allowable singleton exists, play singleton
            if bid value > (bid-round score) and allowable signleton with bid value < .5 exists, play singleton
            else
                if bid value <= (bid-round score), play allowable card with highest bid value
                    but if last player on trick, play lowest allowable card that will take the trick
                if bid value > (bid-round score), play allowable card with highest bid value that *won't* take the trick
            recalculate all bid values
        7. End trick:
            If trumps exist: winner = player of highest trump
            Else winner = player of highest in-suit card
            Winner round score += 1
            Trick leader += 1
        8. End round:
            for each player: ***These need to be tracked outside the "hand" objects!!!***
                if round score == bid: total score += bid + 10
                else total score += round score
            round scores = 0
            bids = 0
            hand_size -= 1
            generate new deck
'''

class Deck:
    """Construct a deck of 52 cards and define shuffling, dealing, and trump selection"""

    suits = ["clubs","diamonds","hearts","spades"]

    def __init__(self):
        """Generate an ordered list of all 52 cards in a standard deck. Trump is set to None on construction"""
        self.cards = []
        for suit in Deck.suits:
            for n in range(0,13):
                card = Card(suit,n)
                self.cards.append(card)
        self.trump = None
        self.shuffled = False

    def __repr__(self):
        if self.shuffled == True:
            isshuff = "is"
        else:
            isshuff = "is not"
        return f"The deck contains {len(self.cards)} cards. It {isshuff} shuffled. Trump is {self.trump}."
    
    def shuffle(self):
        """rewrite the deck instance with its members in a randomized order"""
        random.shuffle(self.cards)
        self.shuffled = True
        print("Deck shuffled!")
    
    def set_trump(self):
        """remove the top card of the deck and set its suit to be trump. return played_cards seed with trump card in it."""
        trump_card = self.cards.pop()
        self.trump = trump_card.suit
        played_cards = {
            "spades": [],
            "hearts": [],
            "diamonds": [],
            "clubs": []
        }
        played_cards[self.trump].append(trump_card)
        print(f"The trump card is the {trump_card.value_name} of {self.trump}.")
        return played_cards
    
    def deal(self,player_stats,hand_size):
        """deals the given number of cards out to the given number of players, drawing from the deck in order."""
        player_list = dict()
        #Construct an empty hand for each player, assigning "Player 1", "Player 2", etc.
        for player,stats in player_stats.items():
            player_list[player] = Hand(player)
            if stats[1]:
                player_list[player].is_lead = True
            if stats[2]:
                player_list[player].is_bot = True
        rounds_dealt = 0
        #Mimic actual dealing order by cycling through players for each card in hand
        while rounds_dealt < hand_size:
            for player,hand in player_list.items():
                card = self.cards.pop()
                hand.cards.append(card)
                card.hand = player
            rounds_dealt += 1
        return player_list
        #not a huge fan of dealing with this as a dictionary; possibly should construct the empty hands outside
        # and pass them in as arguments

class Hand(UserError):
    """store a hand as a list of cards and define sort and compare card actions"""

    def __init__(self,name):
        """Create an empty list, which is filled using Deck.deal."""
        self.cards = []
        self.player = name
        self.is_lead = False
        self.bid_value = 0
        self.round_score = 0
        self.bid = 0
        self.is_bot = False
    
    def __repr__(self):
        repr_string = f"Player: {self.player}\nLeading: {self.is_lead}\nBid value: {self.bid_value}\nThis hand contains:"
        for card in self.cards:
            repr_string += f"\n{card.__repr__()}"
        return repr_string
    
    def __str__(self):
        if self.is_lead:
            leadstr = ""
        else:
            leadstr = " not"
        return_string = f"{self.player} is{leadstr} leading. The hand has bid value {self.bid_value}. Cards in hand:"
        for card in self.cards:
            return_string += f"\n{card.value_name} of {card.suit}. Bid value: {card.bid_value}"
        return return_string
    
    def user_print(self,deck):
        print(f"\nYou bid {self.bid} and have taken {self.round_score}. {(deck.trump).capitalize()} are trump.")
        sorted_hand = []
        suits = ["clubs","diamonds","hearts","spades"]
        for suit in suits:
            micro_sort = self.cards_in_suit(suit)
            micro_sort.sort(key=lambda card: card.value)
            sorted_hand += micro_sort
        print("Cards in your hand:")
        for card in sorted_hand:
            print(f"{card.value_name} of {card.suit}")
    
    #Sort hand method - internal sorting
    
    def cards_in_suit(self,suit):
        """For a given suit, returns a list of cards in hand in that suit"""
        card_list = []
        for card in self.cards:
            if card.suit == suit:
                card_list.append(card)
        return card_list
    
    def set_bid_values(self,deck,played_cards,players,player_list):
        """sets the bid value for each card in hand"""
        self.bid_value = 0
        for card in self.cards:
            if card.istrump(deck):
                card_bid = card.p_trump_win(played_cards,player_list) # this sets card bid value
                self.bid_value += card_bid
            else:
                card.p_in_suit_win(deck,players,played_cards,player_list)
        for card in self.cards:
            if not card.istrump(deck):
                p_suit_led = card.p_suit_led(played_cards,player_list)
                card.bid_value = p_suit_led * card.take_trick
                if card.bid_value > 0.25:
                    self.bid_value += card.bid_value
        return self.bid_value

    @staticmethod
    def trump_broken(played_cards,deck):
        """Return a bool representing whether trump has been broken in the current round"""
        trump = deck.trump
        if len(played_cards[trump]) > 1:
            return True
        else:
            return False
    
    def agnostic_allowable(self,broken,deck):
        """Return the set of allowable cards in hand without regards to trick (ie. all cards if trump is broken; all but trump otherwise)"""
        if broken:
            allowable = self.cards
        else:
            allowable = []
            for card in self.cards:
                if card.suit != deck.trump:
                    allowable.append(card)
        return allowable
    
    def ordered_allowable(self,trick,played_cards,deck):
        """Identify cards in hand that can be played in the current trick, and return them ordered by bid value"""
        broken = self.trump_broken(played_cards,deck)
        cards_in_suit = self.cards_in_suit(trick.lead_suit)
        if len(cards_in_suit) > 0:
            allowable = cards_in_suit
        else:
            allowable = self.cards
        allowable.sort(key=lambda card: card.bid_value)
        return allowable
    
    @staticmethod
    def allowable_singletons(allowable):
        """From allowable (for current trick) cards in hand, returns singletons, ordered by bid value"""
        suit_counters = {"clubs":[],"diamonds":[],"hearts":[],"spades":[]}
        for card in allowable:
            suit_counters[card.suit].append(card)
        singletons = []
        for card_list in suit_counters.values():
            if len(card_list) == 1:
                singletons += card_list
        singletons.sort(key=lambda card: card.bid_value)
        return singletons

    def lead_trick(self,played_cards,deck,players,player_list):
        """Play optimum lead card based on bid values and creating voids
        
        1. recalculate all bid values
        2. if bid value <= (bid-round score) and allowable singleton exists, play singleton with highest bid value
        3. if bid value > (bid-round score) and allowable singleton with bid value < .5 exists, play singleton with lowest bid value
        4. else
            4.a. if bid value <= (bid-round score), play allowable card with highest bid value
            4.b if bid value > (bid-round score), play allowable card with lowest bid value
        """
        self.set_bid_values(deck,played_cards,players,player_list)
        broken = self.trump_broken(played_cards,deck)
        allowable = self.agnostic_allowable(broken,deck)
        if not self.is_bot:
            self.user_print(deck)
            card = self.get_user_card(allowable)
            trick = card.lead(self.cards,played_cards,deck)
        else:
            allowable.sort(key=lambda card: card.bid_value)
            singletons = self.allowable_singletons(allowable)
            if len(singletons) > 0:
                least_singleton = singletons[0].bid_value
            else:
                least_singleton = 1
            want_trick = self.bid_value <= (self.bid - self.round_score)
            if want_trick and len(singletons) > 0:
                trick = singletons[-1].lead(self.cards,played_cards,deck)
            elif not want_trick and least_singleton < 0.5:
                trick = singletons[0].lead(self.cards,played_cards,deck)
            else:
                if want_trick:
                    trick = allowable[-1].lead(self.cards,played_cards,deck)
                else:
                    trick = allowable[0].lead(self.cards,played_cards,deck)
        return trick
    
    @staticmethod
    def lowest_winner(card_list,trick,deck):
        """Return the lowest bid value card in the given list that will win the current trick,\
            or the lowest card from the list if none can take the trick"""
        for card in card_list:
            if card.beats(trick.winner,trick.lead_suit,deck):
                return card
        return card_list[0]

    @staticmethod
    def highest_loser(card_list,trick,deck):
        """Return the highest bid value card in the given list that will *not* win the current trick,\
            or None if such a card does not exist"""
        reverse_list = reversed(card_list)
        for card in reverse_list:
            if not card.beats(trick.winner,trick.lead_suit,deck):
                return card
        return None
    
    def follow_trick(self,players,trick,played_cards,deck,player_list):
        """Play optimum allowable card on trick based on reaching bid and creating voids.
        
        2. if bid value <= (bid-round score) and allowable singleton exists:
            2.a. if not last card in trick, play highest singleton
            2.b. if last card in trick, play lowest singleton that will take the trick or lowest singleton if cannot take trick
        3. else
            3.a. if bid value <= (bid-round score):
                3.a.i. if not last card in trick, play allowable card with highest bid value
                3.a.ii. if last player on trick, play lowest allowable card that will take the trick or lowest card if cannot take trick
            3.b. if bid value > (bid-round score)
                3.b.i. if have singleton that won't take trick, play highest bid value singleton that won't take trick
                3.b.ii. if have allowable that won't take the trick, play highest bid value allowable that won't take trick
                3.b.iii. if must take trick, play highest allowable singleton, or highest allowable card if no singleton
        """
        #1. recalculate all bid values
        self.set_bid_values(deck,played_cards,players,player_list)
        broken = self.trump_broken(played_cards,deck)
        allowable = self.ordered_allowable(trick,played_cards,deck)
        if not self.is_bot:
            self.user_print(deck)
            card = self.get_user_card(allowable)
            trick = card.play(self.cards,trick,played_cards,deck,player_list)
        else:
            singletons = self.allowable_singletons(allowable)
            want_trick = self.bid_value <= (self.bid - self.round_score)
            last_card = players - 1 == len(trick.cards)
            #If the hand "wants" the trick and has singletons, attempt to take with singletons or create voids otherwise
            if want_trick and len(singletons) > 0:
                if not last_card:
                    trick = singletons[-1].play(self.cards,trick,played_cards,deck,player_list)
                else:
                    trick = self.lowest_winner(singletons,trick,deck).play(self.cards,trick,played_cards,deck,player_list)
            else:
                #If the hand "wants" the trick and does not have singletons, attempt to take the trick or dump lowest card otherwise
                if want_trick:
                    if not last_card:
                        trick = allowable[-1].play(self.cards,trick,played_cards,deck,player_list)
                    else:
                        trick = self.lowest_winner(allowable,trick,deck).play(self.cards,trick,played_cards,deck,player_list)
                else:
                    #If the hand does not "want" the trick and can slough a singleton, do so
                    losing_singleton = self.highest_loser(singletons,trick,deck)
                    if losing_singleton != None:
                        trick = losing_singleton.play(self.cards,trick,played_cards,deck,player_list)
                    else:
                        #If the hand does not "want" the trick and can't slough a singleton, play the highest card that won't take the trick
                        losing_card = self.highest_loser(allowable,trick,deck)
                        if losing_card != None:
                            trick = losing_card.play(self.cards,trick,played_cards,deck,player_list)
                        #If the hand does not "want" the trick but can't avoid taking it, play the highest singleton if exists or highest card otherwise
                        elif len(singletons) > 0:
                            trick = singletons[-1].play(self.cards,trick,played_cards,deck,player_list)
                        else:
                            trick = allowable[-1].play(self.cards,trick,played_cards,deck,player_list)
        return trick #will be a hand if the trick is over

    @staticmethod
    def user_card_select():
        """Prompt the user for a suit and value to select a card"""
        card_nums = ["2","3","4","5","6","7","8","9","10"]
        card_royals = ["Jack", "Queen", "King", "Ace"]
        card_val = input('Enter the value of the card you want to play (2 - 10 or "Jack", "Queen", "King", "Ace"): ').capitalize()
        while card_val not in card_nums and card_val not in card_royals:
            print(f"Sorry; {card_val} is not a recognized card value.")
            card_val = input('Enter the value of the card you want to play (2 - 10 or "Jack", "Queen", "King", "Ace"): ').capitalize()
        if card_val in card_nums:
            card_val = int(card_val)
        suits = ["clubs", "diamonds", "hearts", "spades"]
        card_suit = input('Enter the suit of the card you want to play ("clubs", "diamonds", "hearts", "spades"): ').lower()
        while card_suit not in suits:
            print(f"Sorry; {card_suit} is not a recognized suit.")
            card_suit = input('Enter the suit of the card you want to play ("clubs", "diamonds", "hearts", "spades"): ').lower()
        return (card_suit,card_val)
        
    def get_user_card(self,allowable):
        """Gets card from user and validates it. Returns a valid and playable card"""
        card_selected = None
        while card_selected == None:
            (card_suit,card_val) = self.user_card_select()
            try:
                for card in self.cards:
                    if card.suit == card_suit and card.value_name == card_val:
                        card_selected = card
                        if card_selected in allowable:
                            return card_selected
                        else:
                            print(f"You are not allowed to play the {card_val} of {card_suit}.")
                            card_selected = None
                            raise UserError()
            except UserError:
                continue
            print(f"You do not have the {card_val} of {card_suit} in your hand.")
        

    '''
        P(card will take a trick) = P(suit is led)*P(card takes trick in suit) OR P(card beats other trump)
            P(suit is led) = (13-[cards played in suit]-[held cards in suit])/(13-[cards played in suit]) + P(you can lead the suit)
                P(you can lead the suit) = 1 if leading hand (cannot be 1 for multiple suits)
                P(you can lead the suit) = P(you take a trick) (again must account for multiple cards...)
                    P(you take a trick) = sum_over_hand(p(card takes trick in suit),p(card beats other trump))/count(cards in hand)
            P(card takes trick in suit) = P(nobody trumps) - ([cards not in hand and not played greater than card]/12)
                P(nobody trumps) = 1 - P(somebody trumps...)
                    P(somebody trumps) = P(someone has a void)*P(they have trump)
                        P(someone has a void) = (0.75^[current hand size])*([number of players]-1)
                        P(they have trump) = [trumps not in your hand and not played]/((12-[trumps played])*[number of players - 1])
            P(card beats other trump) = 1 - [trumps greater than card not in hand and not played]/(12-[trumps in hand or played])
        Keep a global dictionary of played cards, which can be passed to the Hand methods:
            played_cards = {"spades": [], "hearts": [], "diamonds": [], "clubs": []}
            When a card is played, it's added to the list for its suit, and that list is sorted.
    '''

class Card:
    """Construct cards based on suit and value and define card comparison operators"""
    
    value_list = [2,3,4,5,6,7,8,9,10,"Jack","Queen","King","Ace"]

    def __init__(self,suit,val):
        """assign a suit and value to the card object."""
        self.suit = suit
        self.value = val #a numerical value 0-12 corresponding to 2-Ace
        self.value_name = Card.value_list[self.value]
        self.hand = ""
        #following values are set based on hand
        self.take_trick = 0
        self.bid_value = 0
        

    def __repr__(self):
        return f"{self.value_name} of {self.suit}.\
            \nComparative value: {self.value}.\
            \nHand: {self.hand}\
            \nP(take trick) = {self.take_trick}\
            \nBid Value: {self.bid_value}"
    
    def __str__(self):
        return f"This card is a {self.value_name} of {self.suit}. Bid value: {self.bid_value}"
    
    def istrump(self,deck):
        """return a bool representing whether the card is in the trump suit of the current deck."""
        if self.suit == deck.trump:
            return True
        else:
            return False
    
    def follows_suit(self,lead):
        """return a bool representing whether a card is in the lead suit for the current trick"""
        if self.suit == lead:
            return True
        else:
            return False
    
    def __gt__(self,other):
        """defines greater than operator for in-suit comparison ONLY; use .beats to compare cards"""
        if self.value > other.value:
            return True
        else:
            return False
    
    def beats(self,other,lead,deck):
        """return a bool representing whether self beats other played on the current lead card"""
        #set frequently used methods to prevent re-evaluating
        self_trump = self.istrump(deck)
        other_trump = other.istrump(deck)
        self_follows = self.follows_suit(lead)
        other_follows = other.follows_suit(lead)
        #if suits are the same and trump or following, the higher wins; otherwise both lose
        if self.suit == other.suit:
            if self_trump == False and self_follows == False:
                return false
            else:
                return self > other
        else:
            #if one is trump, that card wins
            if self_trump == True or other_trump == True:
                return self_trump
            #if one follows suit (given neither is trump), that card wins
            elif self_follows or other_follows:
                return self_follows
            #if neither follows suit or is trump, both lose. Just returning False should work here.
            else:
                return False
    
    def get_hand(self,player_list):
        """returns the hand object cotnaining the card, if any"""
        return player_list[self.hand]
    
    #Set bidding value per card
    
    def higher_cards(self,played_cards,player_list):
        """returns the number of higher in-suit cards remaining unplayed and not in hand"""
        played_in_suit = played_cards[self.suit]
        hand = self.get_hand(player_list)
        held_in_suit = hand.cards_in_suit(self.suit)
        known_cards = played_in_suit + held_in_suit
        known_cards.sort(key=lambda card: card.value)
        position = known_cards.index(self)
        known_higher = len(known_cards[position+1:])
        all_higher = 12 - self.value
        return all_higher - known_higher

    def other_in_suit(self,played_cards,suit,player_list):
        """returns the number of cards in a suit that are not in hand and not played"""
        hand = self.get_hand(player_list)
        suit_held = len(hand.cards_in_suit(suit))
        suit_played = len(played_cards[suit])
        n = 13 - suit_held - suit_played
        return n
    
    def p_in_suit_win(self,deck,players,played_cards,player_list):
        """given a card follows suit, return the probability it takes the trick and store that value on the card"""
        #P(card takes trick in suit) = P(nobody trumps) - ([cards not in hand and not played greater than card]/[cards not in hand and not played])
            #P(nobody trumps) = 1 - P(somebody trumps...)
                #P(somebody trumps) = P(someone has a void)*P(they have trump)
                    #P(someone has a void) = (0.75^[current hand size])*([number of players]-1)
                    #P(they have trump) = [trumps not in your hand and not played]/((13-[trumps played])*[number of players - 1])
        suit = self.suit
        hand = self.get_hand(player_list)
        p_void = (4*(0.75**len(hand.cards)))*(players-1)
        #print("p_void:",p_void)
        trump = deck.trump
        other_trump = self.other_in_suit(played_cards,trump,player_list)
        #print("other_trump:",other_trump)
        trump_played = len(played_cards[trump])
        #print("trump_played:",trump_played)
        p_other_trump = other_trump/(max(1,(13-trump_played))*(players-1))
        #print("p_other_trump:",p_other_trump)
        p_not_trumped = 1 - (p_void * p_other_trump)
        #print("p_not_trumped:",p_not_trumped)
        other_in_suit = self.other_in_suit(played_cards,self.suit,player_list)
        if other_in_suit == 0:
            p_outmatched = 1
        else:
            p_outmatched = self.higher_cards(played_cards,player_list)/(other_in_suit)
        #print("p_outmatched:",p_outmatched)
        p = p_not_trumped - p_outmatched
        self.take_trick = p
        return p
    
    def p_trump_win(self,played_cards,player_list):
        """given a card is trump, the return probibility it takes a trick and store that value on the card. The value is also the bid value."""
        #P(card beats other trump) = 1 - [trumps greater than card not in hand and not played]/(13-[trumps in hand or played])
        higher_trumps = self.higher_cards(played_cards,player_list)
        other_trumps = max(1,self.other_in_suit(played_cards,self.suit,player_list))
        p = 1 - (higher_trumps/other_trumps)
        self.take_trick = p
        self.bid_value = p
        return p
    
    def p_suit_led(self,played_cards,player_list):
        """returns the probability that the card's suit is led at some point in the game
        
        Should be run only after the take_trick value is set for all cards in hand
        """
        #P(suit is led) = (13-[cards played in suit]-[held cards in suit])/([hand size]*[other players]) + P(you can lead the suit)
                #P(you can lead the suit) = 1 if leading hand (cannot be 1 for multiple suits)
                #P(you can lead the suit) = P(you take a trick) (again must account for multiple cards...)
                    #P(you take a trick) = sum_over_hand(p(card takes trick in suit),p(card beats other trump))/count(cards in hand)
        hand = self.get_hand(player_list)
        other_in_suit = self.other_in_suit(played_cards,self.suit,player_list)
        played_in_suit = len(played_cards[self.suit])
        p_other_leads = other_in_suit/(len(hand.cards)*len(player_list))
        total_p = 0
        for card in hand.cards:
            total_p += card.take_trick
        if hand.is_lead == True:
            total_p += 1
        p_you_lead = total_p/len(hand.cards)
        #print("p_you_lead:",p_you_lead)
        p = p_other_leads + p_you_lead
        return p
    
    def play(self,hand_cards,trick,played_cards,deck,player_list):
        """play the card on the trick and update trick winner. if last player, end trick and return winning hand."""
        hand_cards.remove(self)
        played_cards[self.suit].append(self)
        trick.cards.append(self)
        print(f"{self.hand} played {self.value_name} of {self.suit}.")
        if len(trick.cards) == len(player_list):
            trick.check_winner(deck)
            winning_hand = trick.end(player_list)
            return winning_hand
        else:
            trick.check_winner(deck)
            return trick

    def lead(self,hand_cards,played_cards,deck):
        """play the lead card to initiate a trick"""
        hand_cards.remove(self)
        played_cards[self.suit].append(self)
        trick = Trick(self)
        print(f"{self.hand} led {self.value_name} of {self.suit}.")
        trick.check_winner(deck)
        return trick

class Trick:
    """Holder for tricks with methods to determine winner"""

    def __init__(self,lead):
        self.cards = [lead]
        self.lead_suit = lead.suit
        self.winner = lead
    
    def __repr__(self):
        return f"This is a trick with lead suit {self.lead_suit} and current winner {self.winner}.\nCards played: {self.cards}"

    def __str__(self):
        string = "\nCards on the table:"
        for card in self.cards:
            string += f"\n{card.hand}'s {card.value_name} of {card.suit}"
        string += f"\nCurrently taking the trick: {self.winner.hand}'s {self.winner.value_name} of {self.winner.suit}"
        return string
    
    def check_winner(self,deck):
        """Check all cards currently in trick against the winner, and sets a new winner if needed"""
        for card in self.cards:
            if card.beats(self.winner,self.lead_suit,deck):
                self.winner = card
        print(self)

    def end(self,player_list):
        """Updates players' round scores and sets the next trick leader"""
        winning_player = self.winner.hand
        winning_hand = player_list[winning_player]
        winning_hand.round_score += 1
        for hand in player_list.values():
            hand.is_lead = False
        winning_hand.is_lead = True
        print(f"\n{winning_player} took the trick! {winning_player} leads next.")
        return winning_hand