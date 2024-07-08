import matplotlib.pyplot as plt
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.conf import settings
from poker_analysis import process_poker_hand, save_to_csv
from .models import Hero

from waiting_room_param import players_list, configurations_table, read_config
from .forms import HeroForm, GameConfigForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from poker_app.pypokergui.utils.card_utils import _pick_unused_card
from poker_app.pypokergui.engine.table import Table
from poker_app.pypokergui.engine.pay_info import PayInfo
from poker_app.pypokergui.engine.player import Player
from poker_app.pypokergui.engine.data_encoder import DataEncoder
from poker_app.pypokergui.engine_wrapper import EngineWrapper
import poker_app.pypokergui.server.game_manager as GM
from poker_app.pypokergui.server.poker import setup_config
from uuid import uuid4


def home(request):
    context = {}
    Hero.objects.all().delete()
    return render(request, 'home.html', context)


def handhistory(request):
    FILES_PATH = 'hh/*.txt'
    hands = process_poker_hand(FILES_PATH)
    poker_hands = []
    for hand_data in hands:
        poker_hands.append(hand_data)

    return render(request, 'handhistory.html', {'poker_hands': poker_hands})


def charts(request):
    FILES_PATH = 'hh/*.txt'
    hands = process_poker_hand(FILES_PATH)

    save_to_csv(hands)
    df = pd.read_csv('poker_hand.csv')
    df['cumulative_win_loss'] = df['win_loss'].cumsum()
    plt.figure(figsize=(15, 4))
    plt.plot(df.index, df['cumulative_win_loss'])
    plt.title('Wykres sumy kumulacyjnej win_loss')
    plt.xlabel('Numer rozdania')
    plt.ylabel('Suma kumulacyjna win_loss')
    plt.grid(True)

    plot_filename = 'poker_hand.png'
    plot_path = os.path.join(settings.MEDIA_ROOT, plot_filename)
    # plot_path = os.path.join('media', 'poker_hand.png')

    plt.savefig(plot_path)
    plt.close()

    plot_url = os.path.join(settings.MEDIA_URL, plot_filename)
    return render(request, 'charts.html', {'plot_url': plot_url})
    # return render(request, 'charts.html', {'plot_path': plot_path})


global_game_manager = GM.GameManager()
def waiting_room_view(request):
    
    form_config_table_data = {}
    file_path = 'poker_app/config_players.txt'
    config_players = read_config(file_path)
    players = players_list(config_players)

    if request.method == 'POST':
        cache.clear()
        form = HeroForm(request.POST)
        form_config_table = GameConfigForm(request.POST)
        
        if form_config_table.is_valid():
            config_data = form_config_table.cleaned_data
            initial_stack = config_data.get('initial_stack')
            small_blind = config_data.get('small_blind')
            ante = config_data.get('ante')
            
            form_config_table_data = {
                'initial_stack': initial_stack,
                'small_blind': small_blind,
                'ante': ante,
            }

        else:
            print("Form is not valid")
            print(form_config_table.errors)

        default_config_table = configurations_table({})
        form_config_table = request.session['form_config_table']

        game_config = {
    'max_round': 10,
    'initial_stack': form_config_table_data.get('initial_stack', default_config_table['initial_stack']),
    'small_blind': form_config_table_data.get('small_blind', default_config_table['small_blind']),
    'ante': form_config_table_data.get('ante', default_config_table['ante']),
    'blind_structure': '',
    'ai_players': players
}
        setup_config(game_config)

        if form.is_valid():
            hero = form.save(commit=False)
            hero.save()
            display_id = len(players)
            players.append({
                'idx': display_id,
                'type': 'human',
                'name': hero.name,
            })
            request.session['players'] = players
            global_game_manager.join_human_player(hero.name, 5)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'poker', {
                    'type': 'register_player',
                    'message': {
                        'name': hero.name,
                    }
                }
            )
            return redirect('hero_registration')
        # engine = EngineWrapper()
        # latest_messages = engine.start_game(players, game_config)

    else:
        form = HeroForm()
        form_config_table = GameConfigForm()

    return render(request, 'waiting_room.html', {
        'form': form,
        'form_config_table': form_config_table,
        'players': players,
    })



def start_game_view(request):
    cache.clear()
    players = request.session.get('players', [])
    
    table = Table()
    community_cards = [str(card) for card in table.get_community_card()]
    pot = 0 # DataEncoder.encode_pot(players)
    # engine = EngineWrapper()
    # latest_messages = engine.start_game(players, game_config)
    dealer_pos = table.dealer_btn
    small_blind_pos = (table.dealer_btn + 1) % len(players)
    big_blind_pos = (table.dealer_btn + 2) % len(players)
    next_player = (big_blind_pos + 1) % len(players)
    round_state = {
        'seats': players,
        'community_card': community_cards,
        'pot': pot,
        'next_player': next_player,
        'dealer_pos': dealer_pos,
        'small_blind_pos': small_blind_pos,
        'big_blind_pos': big_blind_pos
    }
    used_cards = [] 
    hole_card = _pick_unused_card(card_num=2, used_card=used_cards)

    if request.method == 'POST':
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'poker', {
                'type': 'start_game',
                # 'message': latest_messages
            }
        )
        return redirect('start_game')
    
    return render(request, 'start_game.html', {
        'round_state': round_state,
        'players': players,
        'hole_card': hole_card,
    })
