from functools import reduce


class ActionChecker:

  @classmethod
  def correct_action(cls, players, player_pos, sb_amount, action, amount=None):
    if cls.is_allin(players[player_pos], action, amount):
      amount = players[player_pos].stack + players[player_pos].paid_sum()
    elif cls.__is_illegal(players, player_pos, sb_amount, action, amount):
      action, amount = "fold", 0
    elif action == 'check':
      last_raise = cls.__fetch_last_raise(players)
      if last_raise is None:
        action, amount = "check", 0
    return action, amount



  @classmethod
  def is_allin(cls, player, action, bet_amount):
    # Jeśli bet_amount jest słownikiem, weź maksymalną wartość
    if isinstance(bet_amount, dict):
        bet_amount = bet_amount.get('max')  # Weź pod uwagę maksymalną wartość zakładu
   
    # Sprawdzenie all-in dla akcji call
    if action == 'call':
        return bet_amount >= player.stack + player.paid_sum()
    
    # Sprawdzenie all-in dla akcji raise
    elif action == 'raise':
        return bet_amount == player.stack + player.paid_sum()
    
    elif action == 'all_in':
        return bet_amount == player.stack + player.paid_sum()


    return False



  @classmethod
  def need_amount_for_action(cls, player, amount):
    return amount - player.paid_sum()

 
  @classmethod
  def agree_amount(cls, players):
    last_raise = cls.__fetch_last_raise(players)
    
    if not last_raise:  # Jeśli nie było podbicia, nie ma kwoty do sprawdzenia
        return 0

    agree_amount = last_raise["amount"]
    
    # Sprawdzenie, czy gracz ma wystarczająco dużo żetonów na sprawdzenie
    if agree_amount > players[3].stack:
        # Jeśli nie, gracz idzie all-in, więc wracamy z jego maksymalną kwotą
        return players[3].stack

    return agree_amount



  @classmethod
  def can_check(cls, players):
    last_raise = cls.__fetch_last_raise(players)
    can_check = last_raise is None
    # can_check = last_raise is None or last_raise["amount"] == 0
    return can_check


  @classmethod
  def legal_actions(cls, players, player_pos, sb_amount):
    min_raise = cls.__min_raise_amount(players, sb_amount)+ players[player_pos].paid_sum()
    max_raise = players[player_pos].stack + players[player_pos].paid_sum()
    if max_raise <= min_raise:
      min_raise = max_raise = players[player_pos].stack
    can_check = cls.can_check(players)


    if max_raise == min_raise:
        amount_to_call = min_raise
    else:
        amount_to_call = 0 if can_check else cls.agree_amount(players)

    valid_actions =[]
    valid_actions.append({"action": "fold", "amount": 0})
    if can_check:
      valid_actions.append({"action": "check", "amount": 0})
    if amount_to_call > 0:
      valid_actions.append({"action": "call", "amount": amount_to_call})
    if max_raise >= min_raise:
      valid_actions.append({"action": "raise", "amount": {"min": min_raise, "max": max_raise}})
    valid_actions.append({"action": "all_in", "amount": max_raise})

    return valid_actions

  

  @classmethod
  def _is_legal(cls, players, player_pos, sb_amount, action, amount=None):
    return not cls.__is_illegal(players, player_pos, sb_amount, action, amount)

  @classmethod
  def __is_illegal(cls, players, player_pos, sb_amount, action, amount=None):
    if action == 'fold':
      return False
    elif action == 'check':
      return cls.__is_illegal_check(amount)                          # FIXME: do przerobki
    elif action == 'call':
      return cls.__is_short_of_money(players[player_pos], amount)\
          or cls.__is_illegal_call(players, amount)                  # FIXME: cos nie tak z callem
    elif action == 'raise':
      return cls.__is_short_of_money(players[player_pos], amount) \
          or cls.__is_illegal_raise(players, amount, sb_amount)
    elif action == 'all_in':
      return cls.__is_short_of_money(players[player_pos], amount) \
          or cls.__is_illegal_raise(players, amount, sb_amount)


  @classmethod
  def __is_illegal_call(cls, players, amount):
    return amount != cls.agree_amount(players)


  @classmethod
  def __is_illegal_check(cls, amount):
    # Sprawdzenie czy ilość postawionych pieniędzy nie zgadza się z kwotą do zrównania
    if amount != 0:
        return "Nie możesz czekać, ponieważ musisz dołożyć więcej, aby zrównać stawkę."
    # Zwróć None, jeśli check jest legalny
    return None     #zmieniłem na None


  @classmethod
  def __is_illegal_raise(cls, players, amount, sb_amount):
    return cls.__min_raise_amount(players, sb_amount) > amount


  @classmethod
  def __min_raise_amount(cls, players, sb_amount):
    last_raise = cls.__fetch_last_raise(players)
    if last_raise:
        # Jeśli już jest raise, minimalne podbicie to ostatni raise plus suma już zapłaconych pieniędzy
        min_raise = last_raise["amount"] * 2
    else:
        # Jeśli nie było jeszcze raise, minimalne podbicie to czterokrotność small blinda
        min_raise = sb_amount * 4
    # Uwzględnienie kwoty, którą gracz już zapłacił (np. blind)
    return min_raise


  @classmethod
  def __is_short_of_money(cls, player, amount):
    return player.stack < amount - player.paid_sum()

  @classmethod
  def __fetch_last_raise(cls, players):
    all_histories = [p.action_histories for p in players]
    all_histories = reduce(lambda acc, e: acc + e, all_histories)  # flatten
    raise_histories = [h for h in all_histories if h["action"] in ["BIGBLIND", "RAISE", "all_in"]]
    if len(raise_histories) == 0:
        return None
    else:
        return max(raise_histories, key=lambda h: h["amount"])   # maxby

