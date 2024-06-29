import matplotlib.pyplot as plt
import os
import pandas as pd
from django.shortcuts import render, redirect
from poker_analysis import process_poker_hand, save_to_csv
from .models import Hero
from django.http import JsonResponse
from django.conf import settings
from waiting_room_param import players_list, configurations_table, read_config
from .forms import HeroForm, GameConfigForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from poker_app.pypokergui.utils.card_utils import _pick_unused_card
from poker_app.pypokergui.engine.table import Table
import poker_app.pypokergui.server.game_manager as GM
from poker_app.pypokergui.engine_wrapper import EngineWrapper
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


def waiting_room_view(request):
    # Load configurations
    config_table = configurations_table({})
    config_form = GameConfigForm(initial=config_table)

    file_path = 'poker_app/config_players.txt'
    config_players = read_config(file_path)
    players = players_list(config_players)

    # Set default stack if not present
    for player in players:
        if 'stack' not in player:
            player['stack'] = 100

    if request.method == 'POST':
        config_form = GameConfigForm(request.POST)
        form = HeroForm(request.POST)
        if config_form.is_valid():
            config_table = config_form.cleaned_data

        if form.is_valid():
            hero = form.save(commit=False)
            hero.stack = 100  # Set default stack or use form data if available
            hero.save()

            hero_name = hero.name
            display_id = len(players)

            # Append hero to players list
            players.append({
                'idx': display_id,
                'type': 'Hero',
                'name': hero.name,
                'stack': hero.stack,
            })

            # Save players list to session
            request.session['players'] = players

            # Send message to channel layer
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'poker', {
                    'type': 'register_player',
                    'message': {
                        'name': hero.name,
                        'stack': hero.stack,
                    }
                }
            )

            return redirect('waiting_room')
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = HeroForm()

    return render(request, 'waiting_room.html', {
        'config': config_table,
        'form': form,
        'players': players,
        'config_form': config_form,
    })





def start_game_view(request):
    players = request.session.get('players', [])
    for player in players:
        if 'uuid' not in player:
            player['uuid'] = str(uuid4())
        if 'state' not in player:
            player['state'] = 'participating'
            
    players_info = {player['uuid']: player['name'] for player in players}

    # Konfiguracja gry (ustawienia przykładowe, dostosuj według potrzeb)
    game_config = {
        'ante': 0,
        'blind_structure': {
            1: {'small_blind': 10, 'big_blind': 20, 'ante': 0},
            2: {'small_blind': 15, 'big_blind': 30, 'ante': 0},
            },
        'max_round': 100,
        'initial_stack': 1000,
        
    }
    

    table = Table()
    engine = EngineWrapper()
    latest_messages = engine.start_game(players_info, game_config)
    dealer_pos = table.dealer_btn
    round_state = {
        'seats': players,
        'community_card': ['AS'],
        'pot': {
            'main': {'amount': 100},
        },
        'next_player': 1,
        'dealer_btn': dealer_pos,
        'small_blind_pos': 1,
        'big_blind_pos': 2
    }

    used_cards = [] 
    hole_card = _pick_unused_card(card_num=2, used_card=used_cards)

    if request.method == 'POST':
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'poker', {
                'type': 'start_game',
                'message': latest_messages
            }
        )
        return redirect('start_game')
    
    return render(request, 'start_game.html', {
        'round_state': round_state,
        'players': players,
        'hole_card': hole_card,
    })




