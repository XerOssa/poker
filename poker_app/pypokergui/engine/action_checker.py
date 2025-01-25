from functools import reduce


class ActionChecker:

  @classmethod
  def correct_action(cls, players, player_pos, sb_amount, action, amount=None):
    if cls.is_allin(players[player_pos], action, amount):
      amount = players[player_pos].stack + players[player_pos].paid_sum()
      print("stack ", players[player_pos].stack, "+", "paid ",players[player_pos].paid_sum(), "=", amount, "amount")
    elif cls.__is_illegal(players, player_pos, sb_amount, action, amount):
      print("nielegalne zagranie")
    return action, amount



  @classmethod
  def is_allin(cls, player, action, amount):
    if isinstance(amount, dict):
        amount = amount.get('max')            # Weź pod uwagę maksymalną wartość zakładu
    if action == 'call':
        return amount >= player.stack         #+ player.paid_sum() 
    elif action == 'raise':
        return amount == player.stack         #+ player.paid_sum()
    elif action == 'all_in':
        return amount == player.stack               #       + player.paid_sum()
    return False



  @classmethod
  def need_amount_for_action(cls, player, amount):
    return amount - player.paid_sum()


  @classmethod
  def agree_amount(cls, players):
    last_raise = cls.__fetch_last_raise(players)
    
    if not last_raise:  # If no raise, there's nothing to call
        return 0

    agree_amount = last_raise["amount"]
    return agree_amount  # Return the amount of the last raise

  
  @classmethod
  def can_check(cls, players, player_pos):
    last_raise = cls.__fetch_last_raise(players)
    
    # Sprawdź, czy ostatnim zagraniem był BIGBLIND i czy został postawiony przez aktualnego gracza
    if last_raise and last_raise["action"] == "BIGBLIND" and players[player_pos].uuid == last_raise["uuid"]:
        return True  # Gracz postawił BIG BLIND, nikt nie podbił, więc może checkować

    # Sprawdzenie, czy można checkować, bo nie było podbicia
    can_check = last_raise is None or last_raise["amount"] == 0
    return can_check



  @classmethod
  def can_raise(cls, players, player_pos, sb_amount):
    min_raise = cls.__min_raise_amount(players, sb_amount) + players[player_pos].paid_sum()
    max_raise = players[player_pos].stack + players[player_pos].paid_sum()
    # Sprawdzamy, czy minimalna i maksymalna kwota raise to całkowity stack gracza
    return max_raise >= min_raise


  @classmethod
  def legal_actions(cls, players, player_pos, sb_amount):
    min_raise = cls.__min_raise_amount(players, sb_amount)  # Minimalny raise
    max_raise = players[player_pos].stack  # Maksymalny raise to cały stack gracza

    if max_raise <= min_raise:
        min_raise = max_raise = players[player_pos].stack

    # Sprawdzenie, czy można czekać (jeśli nikt nie podbił)
    can_check = cls.can_check(players, player_pos)
    can_raise = cls.can_raise(players, player_pos, sb_amount)

    # Obliczamy kwotę do sprawdzenia (call), tylko jeśli było podbicie
    if not can_check:
        agree_amount = cls.agree_amount(players)
        player_stack = players[player_pos].stack
        amount_to_call = min(agree_amount, player_stack)
    else:
        amount_to_call = 0  # Jeśli można czekać, nie ma opcji call

    valid_actions = []
    valid_actions.append({"action": "fold", "amount": 0})

    if can_check:
        valid_actions.append({"action": "check", "amount": 0})  # Jeśli można czekać

    if amount_to_call > 0:
        valid_actions.append({"action": "call", "amount": amount_to_call})  # Opcja call tylko jeśli było podbicie

    if can_raise:
        valid_actions.append({"action": "raise", "amount": {"min": min_raise, "max": max_raise}})
    # if can_raise:
    #     valid_actions.append({"action": "all_in", "amount": max_raise})

    return valid_actions


  

  @classmethod
  def _is_legal(cls, players, player_pos, sb_amount, action, amount=None):
    return not cls.__is_illegal(players, player_pos, sb_amount, action, amount)

  @classmethod
  def __is_illegal(cls, players, player_pos, sb_amount, action, amount=None):
    if action == 'fold':
      return False
    elif action == 'check':
      return cls.__is_illegal_check(amount)
    elif action == 'call':
      return cls.__is_illegal_call(players, amount, player_pos)
    elif action == 'raise':
      return cls.__is_short_of_money(players[player_pos], amount) \
          or cls.__is_illegal_raise(players, amount, sb_amount)
    elif action == 'all_in':
      return False


  @classmethod
  def __is_illegal_call(cls, players, amount, player_pos):
    # Pobierz wymaganą kwotę do sprawdzenia
    agree_amount = cls.agree_amount(players)# - players[player_pos].paid_sum()
    
    # if players[player_pos].paid_sum():
    #    agree_amount = cls.agree_amount(players) - players[player_pos].paid_sum()
    # Jeśli gracz ma mniej żetonów, call za wszystko jest legalny
    player_stack = players[3].stack
    if amount == player_stack:  # All-in za mniejszą kwotę
        return False
    return amount != agree_amount


  @classmethod
  def __is_illegal_check(cls, amount):
    # Sprawdzenie czy ilość postawionych pieniędzy nie zgadza się z kwotą do zrównania
    if amount != 0:
        return "Nie możesz czekać, ponieważ musisz dołożyć więcej, aby zrównać stawkę."
    return False


  @classmethod
  def __is_illegal_raise(cls, players, amount, sb_amount):
    return cls.__min_raise_amount(players, sb_amount) > amount


  @classmethod
  def __min_raise_amount(cls, players, sb_amount):
    last_raise = cls.__fetch_last_raise(players)
    if last_raise:
        min_raise = last_raise["amount"] * 2
    else:
        min_raise = sb_amount * 4
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

