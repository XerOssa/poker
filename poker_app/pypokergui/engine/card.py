import numpy as np
class Card:

  CLUB = 2
  DIAMOND = 4
  HEART = 8
  SPADE = 16

  SUIT_MAP = {
      2  : 'c',       #["♠", "♥", "♦", "♣"]
      4  : 'd',
      8  : 'h',
      16 : 's'
  }

  RANK_MAP = {
      2  :  '2',
      3  :  '3',
      4  :  '4',
      5  :  '5',
      6  :  '6',
      7  :  '7',
      8  :  '8',
      9  :  '9',
      10 :  'T',
      11 :  'J',
      12 :  'Q',
      13 :  'K',
      14 :  'A'
  }


  def __init__(self, suit, rank):
    self.suit = suit
    self.rank = 14 if rank == 1 else rank

  def __eq__(self, other):
    return self.suit == other.suit and self.rank == other.rank

  def __str__(self):
    suit = self.SUIT_MAP[self.suit]
    rank = self.RANK_MAP[self.rank]
    return "{0}{1}".format(rank, suit)

  def to_id(self):
    rank = 1 if self.rank == 14 else self.rank
    num = 0
    tmp = self.suit >> 1
    while tmp&1 != 1:
      num += 1
      tmp >>= 1

    return rank + 13 * num

  @classmethod
  def from_id(cls, card_id):
    suit, rank = 2, card_id
    while rank > 13:
      suit <<= 1
      rank -= 13

    return cls(suit, rank)

  @classmethod
  def from_str(cls, str_card):
    assert(len(str_card)==2)
    inverse = lambda hsh: {v:k for k,v in hsh.items()}
    suit = inverse(cls.SUIT_MAP)[str_card[0].upper()]
    rank = inverse(cls.RANK_MAP)[str_card[1]]
    return cls(suit, rank)


percentage_table = {
    "AAo" : 0.005, "AKs": 0.035, "AQs": 0.040, "AJs": 0.055, "ATs": 0.060, "A9s": 0.085, "A8s": 0.105, "A7s": 0.120, "A6s": 0.155, "A5s": 0.155, "A4s": 0.170, "A3s": 0.205, "A2s": 0.215,
    "AKo": 0.050, "KKo" : 0.010, "KQs": 0.070, "KJs": 0.085, "KTs": 0.100, "K9s": 0.145, "K8s": 0.180, "K7s": 0.210, "K6s": 0.240, "K5s": 0.265, "K4s": 0.300, "K3s": 0.350, "K2s": 0.355, 
    "AQo": 0.070, "KQo": 0.115, "QQo" : 0.015, "QJs": 0.120, "QTs": 0.150, "Q9s": 0.185, "Q8s": 0.265, "Q7s": 0.320, "Q6s": 0.350, "Q5s": 0.375, "Q4s": 0.405, "Q3s": 0.415, "Q2s": 0.470,
    "AJo": 0.080, "KJo": 0.140, "QJo": 0.195, "JJo" : 0.020, "JTs": 0.210, "J9s": 0.295, "J8s": 0.335, "J7s": 0.400, "J6s": 0.445, "J5s": 0.480, "J4s": 0.520, "J3s": 0.530, "J2s": 0.545, 
    "ATo": 0.105, "KTo": 0.175, "QTo": 0.235, "JTo": 0.315, "TTo" : 0.025, "T9s": 0.335, "T8s": 0.400, "T7s": 0.445, "T6s": 0.525, "T5s": 0.545, "T4s": 0.590, "T3s": 0.615, "T2s": 0.635,
    "A9o": 0.145, "K9o": 0.225, "Q9o": 0.295, "J9o": 0.385, "T9o": 0.430, "99o" : 0.030, "98s": 0.425, "97s": 0.525, "96s": 0.560, "95s": 0.615, "94s": 0.665, "93s": 0.700, "92s": 0.710,
    "A8o": 0.165, "K8o": 0.285, "Q8o": 0.375, "J8o": 0.455, "T8o": 0.510, "98o": 0.560, "88o" : 0.035, "87s": 0.540, "86s": 0.610, "85s": 0.655, "84s": 0.715, "83s": 0.760, "82s": 0.785,
    "A7o": 0.200, "K7o": 0.345, "Q7o": 0.440, "J7o": 0.515, "T7o": 0.585, "97o": 0.620, "87o": 0.675, "77o" : 0.055, "76s": 0.650, "75s": 0.675, "74s": 0.745, "73s": 0.790, "72s": 0.895, 
    "A6o": 0.255, "K6o": 0.365, "Q6o": 0.480, "J6o": 0.605, "T6o": 0.635, "96o": 0.720, "86o": 0.735, "76o": 0.770, "66o" : 0.090, "65s": 0.715, "64s": 0.760, "63s": 0.840, "62s": 0.895, 
    "A5o": 0.250, "K5o": 0.395, "Q5o": 0.500, "J5o": 0.630, "T5o": 0.695, "95o": 0.705, "85o": 0.800, "75o": 0.820, "65o": 0.850, "55o" : 0.145, "54s": 0.780, "53s": 0.840, "52s": 0.900,
    "A4o": 0.275, "K4o": 0.415, "Q4o": 0.550, "J4o": 0.645, "T4o": 0.740, "94o": 0.810, "84o": 0.850, "74o": 0.895, "64o": 0.905, "54o": 0.900, "44o" : 0.230, "43s": 0.855, "42s": 0.900,
    "A3o": 0.305, "K3o": 0.465, "Q3o": 0.575, "J3o": 0.660, "T3o": 0.745, "93o": 0.830, "83o": 0.900, "73o": 0.930, "63o": 0.950, "53o": 0.940, "43o": 0.960, "33o" : 0.320, "32s": 0.910, 
    "A2o": 0.345, "K2o": 0.490, "Q2o": 0.600, "J2o": 0.685, "T2o": 0.800, "92o": 0.900, "82o": 0.915, "72o": 0.970, "62o": 0.990, "52o": 0.980, "42o": 0.995, "32o": 0.995, "22o" : 0.420
}

preflop_ranges = {
    "EP": 0.17,
    "MP": 0.20,
    "CO": 0.30,
    "BTN": 0.46,
    "SB": 0.52,
    "BB": 0
}

def get_range(position):
    return preflop_ranges.get(position.upper(), "Nieznana pozycja")


def get_hands_in_range(percentage_table, min_value, max_value):
    hands_in_range = {}
    
    for hand, value in percentage_table.items():
        if min_value <= value <= max_value:
            hands_in_range[hand] = value
            
    return hands_in_range


def processed_hand(hole_card, percentage_table):
    rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10,
                  'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    rank1, suit1 = hole_card[0]
    rank2, suit2 = hole_card[1]
    
    # Determine if the hand is suited
    suited = suit1 == suit2 and rank1 != rank2

    # Sort ranks based on rank_order values
    sorted_ranks = sorted([rank1, rank2], key=lambda r: rank_order[r], reverse=True)
    ranks_sorted = ''.join(sorted_ranks)

    # Construct the hand key
    hand_key = f"{ranks_sorted}{'s' if suited else 'o'}"

    # Retrieve strength from the percentage table
    strength_hand = percentage_table.get(hand_key, 1)  # Default to 1 if key is not found
    return strength_hand



def is_in_range(hole_card, preflop_ranges):
  strength_hand = processed_hand(hole_card, percentage_table)
  return percentage_table.get(strength_hand, 1) <= preflop_ranges



