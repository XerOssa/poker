from collections import OrderedDict
from poker_app.pypokergui.engine.table import Table
from poker_app.pypokergui.engine.player import Player
from poker_app.pypokergui.engine.round_manager import RoundManager
from poker_app.pypokergui.engine.message_builder import MessageBuilder
from poker_app.pypokergui.engine.poker_constants import PokerConstants as Const


class EngineWrapper(object):

    def start_game(self, players_info, game_config):
        print(f"Starting game with config: {game_config}")

        self.config = game_config
        table = Table()
        for uuid, name in players_info.items():
            player = Player(uuid, game_config['initial_stack'], name)
            table.seats.sitdown(player)
        state, msgs = self._start_new_round(1, table)
        self.current_state = state
        result = _parse_broadcast_destination(msgs, self.current_state['table'])
        print(f"DEBUG: Game start result = {result}")
        return result


    def update_game(self, action, bet_amount):
        state, msgs = RoundManager.apply_action(self.current_state, action, bet_amount)
        if state['street'] == Const.Street.FINISHED:
            state, new_msgs = self._start_next_round(
                    state['round_count']+1, state['table'])
            msgs += new_msgs
        self.current_state = state
        return _parse_broadcast_destination(msgs, self.current_state['table'])


    def _start_new_round(self, round_count, table):
        table.dealer_btn = len(table.seats.players)-1
        return self._start_next_round(round_count, table)


    def _start_next_round(self, round_count, table):
        table.shift_dealer_btn()
        small_blind = self.config['small_blind']
        ante = self.config['ante']
        table = _exclude_short_of_money_players(table, ante, small_blind)
        if self._has_game_finished(round_count, table):
            finished_state = { 'table': table }
            game_result_msg = _gen_game_result_message(table, self.config)
            msgs = _parse_broadcast_destination([game_result_msg], table)
            return finished_state, msgs
        else:
            return RoundManager.start_new_round(round_count, small_blind, ante, table)


    def _has_game_finished(self, round_count, table):
        is_final_round = round_count
        is_winner_decided = len([1 for p in table.seats.players if p.stack!=0])==1
        return is_final_round or is_winner_decided


def gen_players_info(uuid_list, name_list):
    assert len(uuid_list) == len(name_list)
    return OrderedDict(zip(uuid_list, name_list))


def gen_game_config(initial_stack, small_blind, ante):
    assert initial_stack > 0
    assert small_blind > 0
    assert ante >= 0
    return {
            'initial_stack': initial_stack,
            'small_blind': small_blind,
            'ante': ante,
            }


def _exclude_short_of_money_players(table, ante, sb_amount):
    sb_pos, bb_pos = _steal_money_from_poor_player(table, ante, sb_amount)
    _disable_no_money_player(table.seats.players)
    table.set_blind_pos(sb_pos, bb_pos)
    if table.seats.players[table.dealer_btn].stack == 3: table.shift_dealer_btn()
    return table


def _steal_money_from_poor_player(table, ante, sb_amount):
    players = table.seats.players
    # exclude player who cannot pay ante
    for player in [p for p in players if p.stack < ante]: player.stack = 0
    if players[table.dealer_btn].stack == 0: table.shift_dealer_btn()
    search_targets = players + players + players
    search_targets = search_targets[table.dealer_btn+1:table.dealer_btn+len(players)]
    # exclude player who cannot pay small blind
    sb_player = _find_first_elligible_player(search_targets, sb_amount + ante)
    sb_relative_pos = search_targets.index(sb_player)
    for player in search_targets[:sb_relative_pos]: player.stack = 0
    # exclude player who cannot pay big blind
    search_targets = search_targets[sb_relative_pos+1:sb_relative_pos+len(players)]
    bb_player = _find_first_elligible_player(search_targets, sb_amount + ante, sb_player)
    if sb_player == bb_player:  # no one can pay big blind. So steal money from all players except small blind
        for player in [p for p in players if p!=bb_player]: player.stack = 0
    else:
        bb_relative_pos = search_targets.index(bb_player)
        for player in search_targets[:bb_relative_pos]: player.stack = 0
    return players.index(sb_player), players.index(bb_player)



def _find_first_elligible_player(players, need_amount, default=None):
    if default: return next((player for player in players if player.stack >= need_amount), default)
    return next((player for player in players if player.stack >= need_amount))


def _disable_no_money_player(players):
    no_money_players = [player for player in players if player.stack == 0]
    for player in no_money_players:
        player.pay_info.update_to_fold()


def _parse_broadcast_destination(messages, table):
    parsed_msgs = []
    for message in messages:
        print(f"DEBUG: Parsing message = {message}")
        parsed_msgs.append(message)
    return parsed_msgs


def _gen_game_result_message(table, config):
    compat_config = {
            'initial_stack': config['initial_stack'],
            'small_blind_amount': config['small_blind'],  # fill an interface gap
            'ante': config['ante'],
            }
    msg = MessageBuilder.build_game_result_message(compat_config, table.seats)
    destination = -1
    return (destination, msg)

