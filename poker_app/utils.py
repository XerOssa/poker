from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags



def _gen_game_update_message(message):
    message_type = message['message']['message_type']
    content = {'update_type': message_type}
    
    if 'round_start_message' == message_type:
        round_count = message['message']['round_count']
        hole_card = message['message']['hole_card']
        content.update({
            'round_count': round_count,
            'hole_card': hole_card
        })

    elif 'street_start_message' == message_type:
        round_state = message['message']['round_state']
        street = message['message']['street']
        content.update({
            'round_state': round_state,
            'street': street
        })

    elif 'game_update_message' == message_type:
        round_state = message['message']['round_state']
        action = message['message']['action']
        action_histories = message['message']['action_histories']
        content.update({
            'round_state': round_state,
            'action': action,
            'action_histories': action_histories
        })

    elif 'round_result_message' == message_type:
        round_state = message['message']['round_state']
        hand_info = message['message']['hand_info']
        winners = message['message']['winners']
        round_count = message['message']['round_count']
        content.update({
            'round_state': round_state,
            'hand_info': hand_info,
            'winners': winners,
            'round_count': round_count
        })

    elif 'game_result_message' == message_type:
        game_info = message['message']['game_information']
        content.update({'game_information': game_info})

    elif 'ask_message' == message_type:
        round_state = message['message']['round_state']
        hole_card = message['message']['hole_card']
        valid_actions = message['message']['valid_actions']
        action_histories = message['message']['action_histories']
        content.update({
            'round_state': round_state,
            'hole_card': hole_card,
            'valid_actions': valid_actions,
            'action_histories': action_histories
        })
    else:
        raise Exception(f"Unexpected message received : {message}")
    
    return content


def _gen_start_game_message(game_manager):
    context = {'config': game_manager}
    html_str = render_to_string('start_game.html', context)
    html = mark_safe(html_str)
    clean_html = strip_tags(html_str)
    return {'message_type': 'start_game', 'html': clean_html}