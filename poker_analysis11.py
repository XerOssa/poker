import glob
import re 
import csv
import action

class PokerHand:
    def __init__(self, Hand_ID: int, stakes: str, date: str, win_loss: float, my_hand: str):
        self.Hand_ID = Hand_ID
        self.stakes = stakes
        self.date = date
        self.win_loss = win_loss
        self.my_hand = my_hand


    def __str__(self) -> str:
        return f"Numer rozdania: {self.Hand_ID}\nStawki: {self.stakes}\nData: {self.date}\nWin/loss: {self.win_loss}\nmy_hand: {self.my_hand}"

def pay_money(text):
    pay_preflop =  action.preflop(text)
    pay_flop =  action.flop(text)
    pay_turn =  action.turn(text)
    pay_river =  action.river(text)
    
    # Zwróć listę wszystkich wartości
    return [pay_preflop, pay_flop, pay_turn, pay_river]

def process_poker_hand(FILES_PATH: str) -> list:
    PREFIX = 'Poker Hand #HD'
    hh_files = glob.glob(FILES_PATH)
    all_hands = []
    for file in hh_files:
        with open(file, 'r') as f:
            text = f.read()
            hands_text = re.findall(fr'{PREFIX}.+?(?={PREFIX}|\Z)', text, re.DOTALL)
            for hand_text in hands_text:
                # Extract information for each hand and create PokerHand objects
                hand = from_text(hand_text)
                all_hands.append(hand)
    return all_hands

def from_text(text: str) -> PokerHand:
    hand_id_match = re.search(fr'{PREFIX}(\d+)', text)
    Hand_ID = int(hand_id_match.group(1))

    stakes_match = re.search(r'Hold\'em No Limit \((.*?)\)', text)
    stakes = stakes_match.group(1)

    date_match = re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', text)
    date = date_match.group()

    pay = pay_money(text)
    if pay is None:
        pay = 0.00
    PREFIX = 'Poker Hand #HD'
    # Wyszukaj wartość win_loss w tekście rozdania
    win_pot_match = re.search(r'Hero collected \$(\d+\.\d+)', text)
    if win_pot_match:
        win_pot = float(win_pot_match.group(1))
    else:
        # Default value for win_loss if no specific action found
        win_pot = 0.00
    blind = 0.00
    if action.big_blind(text):
        blind = action.big_blind(text)
    elif action.small_blind(text):
        blind = action.small_blind(text)
    win_loss = round(win_pot + blind+ float(pay), 2)

    my_hand = action.my_hand(text)

    return PokerHand(Hand_ID, stakes, date, win_loss, my_hand)

def save_to_csv(hands: list):
    filename = 'D:/ROBOTA/python/poker/poker_hand.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Hand_ID', 'stakes', 'date', 'win_loss']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for hand in hands:
            writer.writerow({'Hand_ID': hand.Hand_ID, 'stakes': hand.stakes, 'date': hand.date, 'win_loss': hand.win_loss})
