from poker_app.pypokergui.engine.pay_info import PayInfo
from poker_app.pypokergui.engine.player import Player
import random


class Seats:

  def __init__(self):
    self.players = []

  def sitdown(self, player):
    self.players.append(player)
    random.shuffle(self.players)
    # Sprawdź, czy human jest wśród graczy
    human_index = None
    for idx, p in enumerate(self.players):
        player_name = getattr(p, 'name', None)  # Uzyskanie nazwy gracza z właściwości 'name'
        if player_name == "Jacek":
            human_index = idx
            break
    # Jeśli human jest wśród graczy, przesuń go na 4. miejsce w kolejności
    if human_index is not None and human_index != 3:
        # Jeśli human nie jest na 4. miejscu, zamień go z graczem na 4. miejscu
        self.players[3], self.players[human_index] = self.players[human_index], self.players[3]


  def size(self):
    return len(self.players)

  def count_active_players(self):
    return len([p for p in self.players if p.is_active()])

  def count_ask_wait_players(self):
    return len([p for p in self.players if p.is_waiting_ask()])

  def serialize(self):
    return [player.serialize() for player in self.players] 

  @classmethod
  def deserialize(cls, serial):
    seats = cls()
    seats.players = [Player.deserialize(s) for s in serial]
    return seats

