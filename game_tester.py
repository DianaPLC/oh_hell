import math

def get_play_order(player_name,play_order_base):
    name_list = play_order_base.copy()
    #print(play_order_base is name_list)
    #print(name_list)
    leader_position = name_list.index(player_name)
    if leader_position == 0 or leader_position == len(name_list)-1:
        name_list.remove(player_name)
        play_order = name_list
    else:
        play_order = name_list[leader_position + 1:] + name_list[:leader_position]
    return play_order

def make_bids(player_list,hand_size,play_order_base):
    """Set bids in order from leader"""
        #i. First bid = bid value rounded naively
        #ii. Middle bids =
            #bid value rounded up if (total bid/players who have bid) < (hand size/players);
            #bid value rounded down if (total bid/players who have bid) > (hand size/players);
            #bid value rounded naively if (total bid/players who have bid) == (hand size/players)
        #iii. Last bid =
            #bid value rounded up if ([hand size] - [total bid]) == bid value rounded down
            #bid value rounded down if ([hand size] - [total bid]) == bid value rounded up
            #bid value rounded naively otherwise
    expected = hand_size/len(player_list)
    total_bid = 0
    bids_made = 0
    for player,hand in player_list.items():
        if hand.is_lead:
            player_name = player
            if not hand.is_bot:
                bid = int(input("Enter your bid: "))
            else:
                bid = round(hand.bid_value)
            hand.bid = bid
            total_bid += bid
            bids_made += 1
            print(f"{player_name} bids {bid}.")
    play_order = get_play_order(player_name,play_order_base)
    last_player = play_order.pop()
    for player_name in play_order:
        actual = total_bid/bids_made
        hand = player_list[player_name]
        bid_value = hand.bid_value
        if actual < expected:
            bid = math.ceil(bid_value)
        elif actual > expected:
            bid = math.floor(bid_value)
        else:
            bid = round(bid_value)
        hand.bid = bid
        total_bid += bid
        bids_made += 1
        print(f"{player_name} bids {bid}.")
    last_hand = player_list[last_player]
    high_last_bid = math.ceil(last_hand.bid_value)
    low_last_bid = math.floor(last_hand.bid_value)
    if hand_size - total_bid == high_last_bid:
        bid = low_last_bid
    elif hand_size - total_bid == low_last_bid:
        bid = high_last_bid
    else:
        bid = round(last_hand.bid_value)
    last_hand.bid = bid
    total_bid += bid
    print(f"{last_player} bids {bid}.")
    print(f"Total bid for round: {total_bid} for {hand_size}.")
    return total_bid

def play_trick(player_list,played_cards,deck,players,play_order_base):
    for player,hand in player_list.items():
        if hand.is_lead:
            trick = hand.lead_trick(played_cards,deck,players,player_list)
            player_name = player
            break
    play_order = get_play_order(player_name,play_order_base)
    for player in play_order:
        trick = player_list[player].follow_trick(players,trick,played_cards,deck,player_list)

from card_handlers import Deck
deck = Deck()
deck.shuffle()
played_cards = deck.set_trump()
#next_step = input("Deal Cards? Y/N ").upper()
player_stats = { #"Player Name" : (Game Score, Round Lead, Is Bot)
    "User" : (0,True,False),
    "Player2" : (0,False,True),
    "Player3" : (0,False,True),
    "Player4" : (0,False,True)
}
play_order_base = ["User","Player2","Player3","Player4"]
#if next_step == "Y":
player_list = deck.deal(player_stats,12)
player_list["User"].user_print(deck)
#else:
    #quit()
#next_step = input("Set Bid Values? Y/N ").upper()
#if next_step == "Y":
for hand in player_list.values():
    hand.set_bid_values(deck,played_cards,4,player_list)
    #print(hand)
#else:
#    quit()
next_step = input("Make Bids? Y/N ").upper()
if next_step == "Y":
    make_bids(player_list,12,play_order_base)
else:
    quit()
played_tricks = 0
next_step = input("Play Trick? Y/N ").upper()
while next_step == "Y" and played_tricks < 12:
    play_trick(player_list,played_cards,deck,4,play_order_base)
    played_tricks += 1
    next_step = input("Play Trick? Y/N ").upper()
else:
    score_str = "Hand completed. Final Scores:"
    for player,hand in player_list.items():
        if hand.bid == hand.round_score:
            pts = hand.bid + 10
        else:
            pts = hand.round_score
        score_str += f"\n{player} bid {hand.bid} and made {hand.round_score}. {player} gets {pts}"
    print(score_str)
    quit()