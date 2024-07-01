import matplotlib.pyplot as plt
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from poker_analysis import process_poker_hand, save_to_csv
from .models import Hero
from django.conf import settings
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


def waiting_room_view(request):
    # Load configurations
    default_config_table = configurations_table({})


    file_path = 'poker_app/config_players.txt'
    config_players = read_config(file_path)
    players = players_list(config_players)

    new_form_initial_stack = None
    new_form_small_blind = None
    new_form_ante = None
    hero_name = None

    form = GameConfigForm()
    form_hero = HeroForm()

    if request.method == 'POST':
        form = GameConfigForm(request.POST)
        form_hero = HeroForm(request.POST)

        if form.is_valid(): 
            form_initial_stack = request.POST.get('initial_stack')
            form_small_blind = request.POST.get('small_blind')  # Use 'small_blind' as intended
            form_ante = request.POST.get('ante')

            new_form_initial_stack = form_initial_stack
            new_form_small_blind = form_small_blind
            new_form_ante = form_ante

        if form_hero.is_valid():
            hero_name = form_hero.save(commit=False)
            hero_name.stack = 100
            hero_name.save()

            display_id = len(players)

            players.append({
                'idx': display_id,
                'type': 'Hero',
                'name': hero_name.name,
                'stack': hero_name.stack,
            })

            request.session['players'] = players

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'poker', {
                    'type': 'register_player',
                    'message': {
                        'name': hero_name.name,
                        'stack': hero_name.stack,
                    }
                }
            )

            return redirect('waiting_room')
        if not form.is_valid():
            print(form.errors)  # Print errors for debugging
            return render(request, 'waiting_room.html', {
                'form': form,  # Pass the form with errors to the template
            })
        
    # setup_config(config_table)
    return render(request, 'waiting_room.html', {
        'config': default_config_table,
        'players': players,
        'new_form_initial_stack': new_form_initial_stack,
        'new_form_big_blind': new_form_small_blind,
        'new_form_ante': new_form_ante,
        'form': form,  # Pass the form object to the template context
  })


def start_game_view(request):
    players_data = request.session.get('players', [])
    players = []
    for player_data in players_data:
        if 'uuid' not in player_data:
            player_data['uuid'] = str(uuid4())
        if 'state' not in player_data:
            player_data['state'] = 'participating'
        player = Player(
            uuid=player_data['uuid'],
            name=player_data['name'],
            initial_stack=player_data.get('stack', 1000),  # Ustawienie początkowego stosu
        )
        players.append(player)

    players_info = {player.uuid: player.name for player in players}

    # Konfiguracja gry (ustawienia przykładowe, dostosuj według potrzeb)
    game_config = {
    'max_round': 10,
    'initial_stack': 1000,
    'small_blind': 10,
    'ante': 1,
    'blind_structure': '',
    'ai_players': [
        {'name': 'random_player', 'path': 'D:/ROBOTA/python/poker/poker_app/sample_player/random_player_setupCHECK.py'},
        {'name': 'Tag', 'path': 'D:/ROBOTA/python/poker/poker_app/sample_player/TagCHECK.py'},
        {'name': 'fish', 'path': 'D:/ROBOTA/python/poker/poker_app/sample_player/fish_player_setupCHECK.py'},
        {'name': 'Whale', 'path': 'D:/ROBOTA/python/poker/poker_app/sample_player/fish_player_setupCHECK.py'}
    ]
}
    
    
    table = Table()
    community_cards = [str(card) for card in table.get_community_card()]
    pot = DataEncoder.encode_pot(players)
    engine = EngineWrapper()
    latest_messages = engine.start_game(players_info, game_config)
    dealer_pos = table.dealer_btn
    small_blind_pos = (table.dealer_btn + 1) % len(players)
    big_blind_pos = (table.dealer_btn + 2) % len(players)
    next_player = (big_blind_pos + 1) % len(players)
    round_state = {
        'seats': players_data,
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
                'message': latest_messages
            }
        )
        return redirect('start_game')
    
    return render(request, 'start_game.html', {
        'round_state': round_state,
        'players': players_data,
        'hole_card': hole_card,
    })



