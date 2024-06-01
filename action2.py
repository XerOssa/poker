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
        call_preflop = r'Hero: calls \$(\d+\.\d+)'
        bet_preflop = r'Hero: bets \$(\d+\.\d+)'
        raise_preflop = r'Hero: raises \$(\d+\.\d+)'
        
        action_call_preflop = re.search(call_preflop, preflop_text)
        if action_call_preflop:
            return action_call_preflop.group(1)
            
        action_bet_preflop = re.search(bet_preflop, preflop_text)   
        if action_bet_preflop:
            return action_bet_preflop.group(1)
            
        action_raise_preflop = re.search(raise_preflop, preflop_text)  
        if action_raise_preflop:
            return action_raise_preflop.group(1)

    return '0.00'

    ######################################  FLOP  ########################################


def flop(text):
    flop_start = text.find('*** FLOP ***')
    flop_end = text.find('*** TURN ***')
    flop_text = text[flop_start:flop_end]
    if flop_text:
        call_flop = r'Hero: calls \$(\d+\.\d+)'
        bet_flop = r'Hero: bets \$(\d+\.\d+)'
        raise_flop = r'Hero: raises \$(\d+\.\d+)'
        uncalled_bet = r'Uncalled bet'
        uncalled_bet_flop = re.search(uncalled_bet, flop_text)
        if uncalled_bet_flop:
            return '0.00'
        
        action_call_flop = re.search(call_flop, flop_text)
        if action_call_flop:
            return action_call_flop.group(1)
            
        action_bet_flop = re.search(bet_flop, flop_text)

        if action_bet_flop:
            return action_bet_flop.group(1)
                
        action_raise_flop = re.search(raise_flop, flop_text)  
        if action_raise_flop:
            return action_raise_flop.group(1)
    
    return '0.00'

    ######################################  TURN  ########################################



def turn(text):
    turn_start = text.find('*** TURN ***')
    turn_end = text.find('*** RIVER ***')
    turn_text = text[turn_start:turn_end]
    if turn_text:
        call_turn = r'Hero: calls \$(\d+\.\d+)'
        bet_turn = r'Hero: bets \$(\d+\.\d+)'
        raise_turn = r'Hero: raises \$(\d+\.\d+)'
        uncalled_bet = r'Uncalled bet \(\$([\d.]+)\) returned to Hero'

        action_call_turn = re.search(call_turn, turn_text)
        if action_call_turn:
            return action_call_turn.group(1)
        
        uncalled_bet_turn = re.search(uncalled_bet, turn_text)    
        action_bet_turn = re.search(bet_turn, turn_text)   
        if action_bet_turn:
            return action_bet_turn.group(1)
        if uncalled_bet_turn:
            '0.00'    
        action_raise_turn = re.search(raise_turn, turn_text)  
        if action_raise_turn:
            return action_raise_turn.group(1)
    

    return '0.00'

    ######################################  RIVER  ########################################


def river(text):
    river_start = text.find('*** RIVER ***')
    river_end = text.find('*** SHOWDOWN ***')
    river_text = text[river_start:river_end]
    if river_text:
        call_river = r'Hero: calls \$(\d+\.\d+)'
        bet_river = r'Hero: bets \$(\d+\.\d+)'
        raise_river = r'Hero: raises \$(\d+\.\d+)'
        uncalled_bet = r'Uncalled bet \(\$([\d.]+)\) returned to Hero'

        action_call_river = re.search(call_river, river_text)
        if action_call_river:
            return action_call_river.group(1)
        
        uncalled_bet_river = re.search(uncalled_bet, river_text)    
        action_bet_river = re.search(bet_river, river_text)   
        if action_bet_river:
            return action_bet_river.group(1)
        if uncalled_bet_river:
            '0.00'  

        action_raise_river = re.search(raise_river, river_text)  
        if action_raise_river:
            return action_raise_river.group(1)
    

    return '0.00'

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