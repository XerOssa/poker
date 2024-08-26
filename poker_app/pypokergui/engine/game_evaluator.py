from functools import reduce
from itertools import groupby

from poker_app.pypokergui.engine.hand_evaluator import HandEvaluator
from poker_app.pypokergui.engine.pay_info import PayInfo

class GameEvaluator:

  @classmethod
  def judge(cls, table):
    winners = cls.__find_winners_from(table.get_community_card(), table.seats.players)
    hand_info = cls.__gen_hand_info_if_needed(table.seats.players, table.get_community_card())
    prize_map = cls.__calc_prize_distribution(table.get_community_card(), table.seats.players)
    return winners, hand_info, prize_map

  @classmethod
  def create_pot(cls, players):
    side_pots = cls.__get_side_pots(players)
    main_pot = cls.__get_main_pot(players, side_pots)
    return side_pots + [main_pot]


  @classmethod
  def __calc_prize_distribution(cls, community_card, players):
    prize_map = cls.__create_prize_map(len(players))
    pots = cls.create_pot(players)
    for pot in pots:
      winners = cls.__find_winners_from(community_card, pot["eligibles"])
      if winners:
        prize = int(pot["amount"] / len(winners))
        for winner in winners:
          prize_map[players.index(winner)] += prize
    return prize_map


  @classmethod
  def __create_prize_map(cls, player_num):
    def update(d, other): d.update(other); return d
    return reduce(update, [{i:0} for i in range(player_num)], {})

  @classmethod
  def __find_winners_from(cls, community_card, players):
    score_player = lambda player: HandEvaluator.eval_hand(player.hole_card, community_card)

    active_players = [player for player in players if player.is_active()]
    scores = [score_player(player) for player in active_players]
    if scores:
      best_score = max(scores)
    else:
      print("cos nie tak z podziałem puli")
    score_with_players = [(score, player) for score, player in zip(scores, active_players)]
    winners = [s_p[1] for s_p in score_with_players if s_p[0] == best_score]
    return winners

  @classmethod
  def __gen_hand_info_if_needed(cls, players, community):
    active_players = [player for player in players if player.is_active()]
    gen_hand_info = lambda player: { "uuid": player.uuid, "hand" : HandEvaluator.gen_hand_rank_info(player.hole_card, community) }
    return [] if len(active_players) == 1 else [gen_hand_info(player) for player in active_players]

  @classmethod
  def __get_main_pot(cls, players, sidepots):
    max_pay = max([pay.amount for pay in cls.__get_payinfo(players)])
    return {
        "amount": cls.__get_players_pay_sum(players) - cls.__get_sidepots_sum(sidepots),
        "eligibles": [player for player in players if player.pay_info.amount == max_pay]
    }

  @classmethod
  def __get_players_pay_sum(cls, players):
    return sum([pay.amount for pay in cls.__get_payinfo(players)])

  @classmethod
  def __get_side_pots(cls, players):
    pay_amounts = [payinfo.amount for payinfo in cls.__fetch_allin_payinfo(players)]
    gen_sidepots = lambda sidepots, allin_amount: sidepots + [cls.__create_sidepot(players, sidepots, allin_amount)]
    return reduce(gen_sidepots, pay_amounts, [])

  @classmethod
  def __create_sidepot(cls, players, smaller_side_pots, allin_amount):
    return {
        "amount": cls.__calc_sidepot_size(players, smaller_side_pots, allin_amount),
        "eligibles" : cls.__select_eligibles(players, allin_amount)
    }

  @classmethod
  def __calc_sidepot_size(cls, players, smaller_side_pots, allin_amount):
    add_chip_for_pot = lambda pot, player: pot + min(allin_amount, player.pay_info.amount)
    target_pot_size = reduce(add_chip_for_pot, players, 0)
    return target_pot_size - cls.__get_sidepots_sum(smaller_side_pots)

  @classmethod
  def __get_sidepots_sum(cls, sidepots):
    return reduce(lambda sum_, sidepot: sum_ + sidepot["amount"], sidepots, 0)

  @classmethod
  def __select_eligibles(cls, players, allin_amount):
    return [player for player in players if cls.__is_eligible(player, allin_amount)]

  @classmethod
  def __is_eligible(cls, player, allin_amount):
    return player.pay_info.amount >= allin_amount and \
        player.pay_info.status != PayInfo.FOLDED

  @classmethod
  def __fetch_allin_payinfo(cls, players):
    payinfo = cls.__get_payinfo(players)
    allin_info = [info for info in payinfo if info.status == PayInfo.ALLIN]
    return sorted(allin_info, key=lambda info: info.amount)

  @classmethod
  def __get_payinfo(cls, players):
    return [player.pay_info for player in players]
