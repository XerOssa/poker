from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

def _gen_game_update_message(message):
    message_type = message['message']['message_type']
    content = {'update_type': message_type}

    if 'round_start_message' == message_type:
        round_count = message['message']['round_count']
        hole_card = message['message']['hole_card']
        event_html_str = render_to_string(
            "start_game.html",
            {'round_count': round_count, 'hole_card': hole_card}
        )
        content['event_html'] = event_html_str
    elif 'street_start_message' == message_type:
        round_state = message['message']['round_state']
        street = message['message']['street']
        table_html_str = render_to_string("start_game.html", {'round_state': round_state})
        event_html_str = render_to_string("start_game.html", {'street': street})
        content['table_html'] = table_html_str
        content['event_html'] = event_html_str
    elif 'game_update_message' == message_type:
        round_state = message['message']['round_state']
        action = message['message']['action']
        action_histories = message['message']['action_histories']
        table_html_str = render_to_string("start_game.html", {'round_state': round_state})
        event_html_str = render_to_string("start_game.html", {'action': action, 'round_state': round_state})
        content['table_html'] = table_html_str
        content['event_html'] = event_html_str
    elif 'round_result_message' == message_type:
        round_state = message['message']['round_state']
        hand_info = message['message']['hand_info']
        winners = message['message']['winners']
        round_count = message['message']['round_count']
        table_html_str = render_to_string("start_game.html", {'round_state': round_state})
        event_html_str = render_to_string("start_game.html", {
            'round_state': round_state,
            'hand_info': hand_info,
            'winners': winners,
            'round_count': round_count
        })
        content['table_html'] = table_html_str
        content['event_html'] = event_html_str
    elif 'game_result_message' == message_type:
        game_info = message['message']['game_information']
        event_html_str = render_to_string("start_game.html", {'game_information': game_info})
        content['event_html'] = event_html_str
    elif 'ask_message' == message_type:
        round_state = message['message']['round_state']
        hole_card = message['message']['hole_card']
        valid_actions = message['message']['valid_actions']
        action_histories = message['message']['action_histories']
        table_html_str = render_to_string("start_game.html", {'round_state': round_state})
        event_html_str = render_to_string("start_game.html", {
            'hole_card': hole_card,
            'valid_actions': valid_actions,
            'action_histories': action_histories
        })
        content['table_html'] = table_html_str
        content['event_html'] = event_html_str
    else:
        raise Exception("Unexpected message received : %r" % message)

    return {
        'message_type': 'update_game',
        'content': content
    }

def _gen_start_game_message(handler, game_manager, uuid):
    registered = game_manager.get_human_player_info(uuid)
    context = {
        'config': game_manager,
        'registered': registered
    }
    html_str = render_to_string('start_game.html', context)
    html = mark_safe(html_str)

    return {
        'message_type': 'start_game',
        'html': html
    }