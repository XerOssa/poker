from functools import reduce


class ActionChecker:

  @classmethod
  def correct_action(cls, players, player_pos, sb_amount, action, amount=None):
    if cls.is_allin(players[player_pos], action, amount):
      amount = players[player_pos].stack + players[player_pos].paid_sum()
    elif cls.__is_illegal(players, player_pos, sb_amount, action, amount):
      action, amount = "fold", 0
    elif action == 'check':
        # Jeśli gracz decyduje się na check i nie było żadnego podbicia, pozwól mu zachować swoją rękę
      last_raise = cls.__fetch_last_raise(players)
      if last_raise is None:
        action, amount = "check", 0
    return action, amount

  @classmethod
  def is_allin(cls, player, action, bet_amount):
      if not isinstance(bet_amount, (int, float)):
          raise TypeError(f"Invalid bet_amount: {bet_amount}. Expected a number.")
          
      if action == 'call':
          return bet_amount >= player.stack + player.paid_sum()
      elif action == 'raise':
          return bet_amount == player.stack + player.paid_sum()
      else:
          return False



  @classmethod
  def need_amount_for_action(cls, player, amount):
    return amount - player.paid_sum()

 
  @classmethod
  def agree_amount(cls, players):
    last_raise = cls.__fetch_last_raise(players)
    if last_raise and last_raise["amount"] > players[3].stack:
      return players[3].stack
    else:
      return last_raise["amount"] if last_raise else 0


  @classmethod
  def can_check(cls, players):
    last_raise = cls.__fetch_last_raise(players)
    can_check = last_raise is None or last_raise["amount"] == 0
    return can_check


  @classmethod
  def legal_actions(cls, players, player_pos, sb_amount):
    min_raise = cls.__min_raise_amount(players, sb_amount)
    max_raise = players[player_pos].stack + players[player_pos].paid_sum()
    
    can_check = cls.can_check(players)

    if max_raise <= min_raise:
        min_raise = max_raise = players[player_pos].stack
    
    amount_to_call = cls.agree_amount(players) if not can_check else 0


    valid_actions =[]
    if can_check:
      valid_actions.append({"action": "check", "amount": 0})
    if not can_check:
      valid_actions.append({"action": "fold", "amount": 0})

    if amount_to_call > 0:
      valid_actions.append({"action": "call", "amount": amount_to_call})

    if max_raise >= min_raise:
      valid_actions.append({"action": "raise", "amount": {"min": min_raise, "max": max_raise}})

    return valid_actions

  

  @classmethod
  def _is_legal(cls, players, player_pos, sb_amount, action, amount=None):
    return not cls.__is_illegal(players, player_pos, sb_amount, action, amount)

  @classmethod
  def __is_illegal(cls, players, player_pos, sb_amount, action, amount=None):
    if action == 'fold':
      return False
    elif action == 'check':
      return cls.__is_illegal_check(amount)                          #do przeróbki
    elif action == 'call':
      return cls.__is_short_of_money(players[player_pos], amount)\
          or cls.__is_illegal_call(players, amount)
    elif action == 'raise':
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
    raise_ = cls.__fetch_last_raise(players)
    if raise_:
      
      return raise_["amount"]* 2
    else:
      return sb_amount * 4


  @classmethod
  def __is_short_of_money(cls, player, amount):
    return player.stack < amount - player.paid_sum()

  @classmethod
  def __fetch_last_raise(cls, players):
    all_histories = [p.action_histories for p in players]
    all_histories = reduce(lambda acc, e: acc + e, all_histories)  # flatten
    raise_histories = [h for h in all_histories if h["action"] in ["RAISE", "SMALLBLIND", "BIGBLIND"]]
    if len(raise_histories) == 0:
      return None
    else:
      return max(raise_histories, key=lambda h: h["amount"])  # maxby

