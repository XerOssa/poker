import glob
import re 
import csv
import action

class PokerHand:
    def __init__(self, Hand_ID: int, stakes: str, date: str, my_hand: str, win_loss: float, position: str, line: str):
        self.Hand_ID = Hand_ID
        self.stakes = stakes
        self.date = date
        self.my_hand = my_hand
        self.win_loss = win_loss
        self.position = position
        self.line = line


    def __str__(self) -> str:
        return f"Numer rozdania: {self.Hand_ID}\nStawki: {self.stakes}\nData: {self.date}\nmy_hand: {self.my_hand}\nWin/loss: {self.win_loss}\nPosition: {self.position}\nLine: {self.line}"



def pay_money(text):
    _, pay_preflop = action.preflop(text)
    _, pay_flop = action.flop(text)
    _, pay_turn = action.turn(text)
    _, pay_river = action.river(text)
    
    pay_preflop = float(pay_preflop)
    pay_flop = float(pay_flop)
    pay_turn = float(pay_turn)
    pay_river = float(pay_river)
    
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
                hand = from_text(hand_text)
                all_hands.append(hand)
    return all_hands


def from_text(text: str) -> PokerHand:
    hand_id_match = re.search(fr'{'Poker Hand #HD'}(\d+)', text)
    Hand_ID = int(hand_id_match.group(1))

    stakes_match = re.search(r'Hold\'em No Limit\s+\((.*?)\)', text)
    stakes = stakes_match.group(1)

    date_match = re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', text)
    date = date_match.group()

    blind = 0.00
    if action.big_blind(text):
        blind = float(action.big_blind(text))
    elif action.small_blind(text):
        blind = float(action.small_blind(text))

    my_hand = action.my_hand(text)

    win_pot = float(action.showdown(text) or 0.0)

    pay_list = pay_money(text)
    if all(pay is None for pay in pay_list):
        pay_list = [0.00] * len(pay_list)

    summary = action.summary(text)
    uncalled = float(action.uncalled(text))
    pot = float(summary[0])
    rake = float(summary[1])

    win_loss = round(win_pot - blind- sum(pay_list) + uncalled - rake, 2)

    position = action.position(text)

    line = action.line(text)

    return PokerHand(Hand_ID, stakes, date, my_hand,  win_loss, position, line)

def save_to_csv(hands: list):
    filename = 'D:/ROBOTA/python/poker/poker_hand.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Hand_ID', 'stakes', 'date', 'win_loss']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for hand in hands:
            writer.writerow({'Hand_ID': hand.Hand_ID, 'stakes': hand.stakes, 'date': hand.date, 'win_loss': hand.win_loss})
