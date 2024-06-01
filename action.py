import re

def small_blind(text):
    pay_sb = re.search(r'Hero: posts small blind \$(\d+\.\d+)', text)
    if pay_sb:
        return pay_sb.group(1)

def big_blind(text):
    pay_bb = re.search(r'Hero: posts big blind \$(\d+\.\d+)', text)
    if pay_bb:
        return pay_bb.group(1)
    

def my_hand(text):
    pattern = r'Dealt to Hero \[(\w{2}) (\w{2})\]'
    my_cards = re.search(pattern, text)
    if my_cards:
        return f"{my_cards.group(1)} {my_cards.group(2)}"
    return None


    ###################################  PREFLOP  ###########################################


def preflop(text):
    preflop_start = text.find('*** HOLE CARDS ***')
    preflop_end = text.find('*** FLOP ***')
    preflop_text = text[preflop_start:preflop_end]
    
    if preflop_text:
        if re.search(r'Hero: folds', preflop_text):
            return 'F', '0.00'
        call_preflop = re.search(r'Hero: calls \$(\d+\.\d+)', preflop_text)
        if call_preflop:
            return 'C', call_preflop.group(1)
        check_preflop = re.search(r'Hero: checks', preflop_text)
        if check_preflop:
            return 'X', '0.00'
        bet_preflop = re.search(r'Hero: bets \$(\d+\.\d+)', preflop_text)
        if bet_preflop:
            return 'B', bet_preflop.group(1)
        raise_preflop = re.search(r'Hero: raises \$(\d+\.\d+)', preflop_text)
        if raise_preflop:
            return 'R', raise_preflop.group(1)
    return '', '0.00'

def flop(text):
    flop_start = text.find('*** FLOP ***')
    flop_end = text.find('*** TURN ***')
    flop_text = text[flop_start:flop_end]
    if flop_text:
        if re.search(r'Hero: folds', flop_text):
            return 'F', '0.00'
        call_flop = re.search(r'Hero: calls \$(\d+\.\d+)', flop_text)
        if call_flop:
            return 'C', call_flop.group(1)
        check_flop = re.search(r'Hero: checks', flop_text)
        if check_flop:
            return 'X', '0.00'
        bet_flop = re.search(r'Hero: bets \$(\d+\.\d+)', flop_text)
        if bet_flop:
            return 'B', bet_flop.group(1)
        raise_flop = re.search(r'Hero: raises \$(\d+\.\d+)', flop_text)
        if raise_flop:
            return 'R', raise_flop.group(1)
    return '', '0.00'

def turn(text):
    turn_start = text.find('*** TURN ***')
    turn_end = text.find('*** RIVER ***')
    turn_text = text[turn_start:turn_end]
    if turn_text:
        if re.search(r'Hero: folds', turn_text):
            return 'F', '0.00'
        call_turn = re.search(r'Hero: calls \$(\d+\.\d+)', turn_text)
        if call_turn:
            return 'C', call_turn.group(1)
        check_turn = re.search(r'Hero: checks', turn_text)
        if check_turn:
            return 'X', '0.00'
        bet_turn = re.search(r'Hero: bets \$(\d+\.\d+)', turn_text)
        if bet_turn:
            return 'B', bet_turn.group(1)
        raise_turn = re.search(r'Hero: raises \$(\d+\.\d+)', turn_text)
        if raise_turn:
            return 'R', raise_turn.group(1)
    return '', '0.00'

def river(text):
    river_start = text.find('*** RIVER ***')
    river_end = text.find('*** SHOWDOWN ***')
    river_text = text[river_start:river_end]
    if river_text:
        if re.search(r'Hero: folds', river_text):
            return 'F', '0.00'
        call_river = re.search(r'Hero: calls \$(\d+\.\d+)', river_text)
        if call_river:
            return 'C', call_river.group(1)
        check_river = re.search(r'Hero: checks', river_text)
        if check_river:
            return 'X', '0.00'
        bet_river = re.search(r'Hero: bets \$(\d+\.\d+)', river_text)
        if bet_river:
            return 'B', bet_river.group(1)
        raise_river = re.search(r'Hero: raises \$(\d+\.\d+)', river_text)
        if raise_river:
            return 'R', raise_river.group(1)
    return '', '0.00'

    ######################################  SHOWDOWN  ########################################

def showdown(text):
    showdown_start = text.find('*** SHOWDOWN ***')
    showdown_end = text.find('*** SUMMARY ***')
    showdown_text = text[showdown_start:showdown_end]
    if showdown_text:
        win_pot_match = re.search(r'Hero collected \$(\d+\.\d+)', text)
        if win_pot_match:
            return  win_pot_match.group(1)

    return '0.00'

    ######################################  SUMMARY  ########################################

def summary(text):
    summary_start = text.find('*** SUMMARY ***')
    summary_end = text.find('Board')
    summary_text = text[summary_start:summary_end]
    total_pot_value = '0.00'
    if summary_text:
        if re.search(r'Hero .* collected .*', summary_text):
            total_pot = re.search(r'Total pot \$(\d+\.\d+)', text)
            if total_pot:
                total_pot_value = total_pot.group(1)
            
            rake = re.search(r'Rake \$(\d+\.\d+)', text)
            if rake:
                rake_value = rake.group(1)
            else:
                rake_value = '0.00'
                
            return total_pot_value, rake_value
    
    return '0.00', '0.00'

def uncalled(text):
    uncalled_start = text.find('*** HOLE CARDS ***')
    uncalled_end = text.find('*** SUMMARY ***')
    uncalled_text = text[uncalled_start:uncalled_end]
    if uncalled_text:
        uncalled_bet = re.search(r'Uncalled bet \(\$(\d+\.\d+)\) returned to Hero', uncalled_text)
        if uncalled_bet:
            return uncalled_bet.group(1)
    return '0.00'


def position(text):
    position_start = text.find('Table')
    position_end = text.find('*** HOLE CARDS ***')
    position_text = text[position_start:position_end]
    if position_text:
        seat_button_match = re.search(r'max Seat #(\d+)', text)
        seat_button = int(seat_button_match.group(1))
        seat_hero_match = re.search(r'Seat (\d+): Hero', text)
        seat_hero = int(seat_hero_match.group(1))
        members = len(re.findall(r'chips', text))
        sb_hero = re.search(r'Hero: posts small blind \$(\d+\.\d+)', text)
        bb_hero = re.search(r'Hero: posts big blind \$(\d+\.\d+)', text)
        if seat_button == seat_hero:
            return 'BTN'
        if sb_hero:
            return 'SB'
        if bb_hero:
            return 'BB'
        
        if members == 4:
            if not bb_hero or sb_hero or seat_button:
                return 'CO'
            
        if members == 5:
            co_position = seat_button - 1
            if co_position <= 0:
                co_position = members + seat_button - 1
            mp_position = seat_button - 2
            if mp_position <= 0:
                mp_position = members + seat_button - 1
            if mp_position == seat_hero:
                return 'MP'
            if co_position == seat_hero:
                return 'CO'
            if re.search(r'Seat #1 is the button', text):
                if re.search(r'Seat 6: Hero', text):
                    return 'CO'

        co_position = seat_button - 1
        if co_position <= 0:
            co_position = members + 1
        mp_position = seat_button - 2
        if mp_position <= 0:
            mp_position = members
        utg_position = seat_button - 3
        if utg_position <= 0:
            utg_position = members - 1
            
        if utg_position == seat_hero:
            return 'UTG'
        if mp_position == seat_hero:
            return 'MP'
        if co_position == seat_hero:
            return 'CO'
        if re.search(r'Seat #3 is the button', text):
            if re.search(r'Seat 6: Hero', text):
                return 'EP'
        if re.search(r'Seat #1 is the button', text):
            if re.search(r'Seat 4: Hero', text):
                return 'EP'
    return None

def line(text):
    move_pre, _ = preflop(text)
    move_flop, _ = flop(text)
    move_turn, _ = turn(text)
    move_river, _ = river(text)
    
    return move_pre + move_flop + move_turn + move_river
