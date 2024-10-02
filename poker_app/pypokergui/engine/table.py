from poker_app.pypokergui.engine.card import Card
from poker_app.pypokergui.engine.seats import Seats
from poker_app.pypokergui.engine.deck import Deck
import random

class Table:

    def __init__(self, seats=None, cheat_deck=None):
        self.dealer_btn = 0
        self._blind_pos = None
        self.seats = seats if seats else Seats()
        self.deck = cheat_deck if cheat_deck else Deck()
        self._community_card = []

    def __str__(self):
        num_players = len(self.seats.players)
        community_cards = ', '.join(self._community_card) if self._community_card else 'None'
        return f"Table(Players: {num_players}, Dealer Button: {self.dealer_btn}, Community Cards: {community_cards})"


    def shift_dealer_btn(self):
        # print(f"Shifting dealer button from {self.dealer_btn}")
        self.dealer_btn = self.next_active_player_pos(self.dealer_btn)
        if self.dealer_btn == 0 and any(player.is_active() for player in self.seats.players):
            # self.dealer_btn = random.randint(0, len(self.seats.players) - 1)
            self.dealer_btn = 0
            print(f"New dealer button candidate: {self.dealer_btn}")


    def next_active_player_pos(self, start_pos):
        return self.__find_entitled_player_pos(start_pos, lambda player: player.is_active() and player.stack != 0)

    def set_blind_pos(self, sb_pos, bb_pos):
        self._blind_pos = [sb_pos, bb_pos]

    def __find_entitled_player_pos(self, start_pos, check_method):
        players = self.seats.players
        search_targets = players + players
        search_targets = search_targets[start_pos + 1:start_pos + len(players) + 1]
        assert(len(search_targets) == len(players))
        match_player = next((player for player in search_targets if check_method(player)), None)
        return self._player_not_found if match_player is None else players.index(match_player)

    _player_not_found = "not_found"

    def sb_pos(self):
        if self._blind_pos is None:
            raise Exception("blind position is not yet set")
        return self._blind_pos[0]

    def bb_pos(self):
        if self._blind_pos is None:
            raise Exception("blind position is not yet set")
        return self._blind_pos[1]

    def get_community_card(self):
        return self._community_card[:]

    def add_community_card(self, card):
        if len(self._community_card) == 5:
            pass
        self._community_card.append(card)

    def reset(self):
        self.deck.restore()
        self._community_card = []
        for player in self.seats.players:
            player.clear_holecard()
            player.clear_action_histories()
            player.clear_pay_info()

    def next_ask_waiting_player_pos(self, start_pos):
        return self.__find_entitled_player_pos(start_pos, lambda player: player.is_waiting_ask())

    def serialize(self):
        community_card = [card.to_id() for card in self._community_card]
        return [
            self.dealer_btn, 
            Seats.serialize(self.seats),
            Deck.serialize(self.deck), 
            community_card, 
            self._blind_pos
        ]

    @classmethod
    def deserialize(cls, serial):
        deck = Deck.deserialize(serial[2])
        community_card = [Card.from_id(cid) for cid in serial[3]]
        table = cls(cheat_deck=deck)
        table.dealer_btn = serial[0]
        table.seats = Seats.deserialize(serial[1])
        table._community_card = community_card
        table._blind_pos = serial[4]
        return table

