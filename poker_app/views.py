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
    config_table = configurations_table({})
    config_form = GameConfigForm(initial=config_table)

    file_path = 'poker_app/config_players.txt'
    config_players = read_config(file_path)
    players = players_list(config_players)

    for player in players:
        if 'stack' not in player:
            player['stack'] = 100 
    if request.method == 'POST':
        config_form = GameConfigForm(request.POST)
        form = HeroForm(request.POST)
        if config_form.is_valid():
            config_table = config_form.cleaned_data
        if form.is_valid():
            hero = form.save()
            channel_layer = get_channel_layer()
            display_id = len(players)
            for player in players:
                if 'path' not in player:
                    player['path'] = 'config_players.txt'  # Ustawienie domyślnej ścieżki dla gracza AI
                global_game_manager = GM.GameManager()
                global_game_manager.join_ai_player(player['name'], player['path'])
            print('players pypokergui:', players)

            players.append({
                'idx': display_id,
                'type': 'Hero',
                'name': player['name'],  # Access 'name' using dictionary key
                'stack': player['stack'],
                })
            
            global_game_manager.join_human_player(player['name'],str(display_id))
            # Zapisz listę graczy w sesji
            request.session['players'] = players
            async_to_sync(channel_layer.group_send)(
                'poker', {
                    'type': 'register_player',
                    'message': {
                        'name': player['name'],  # Access 'name' using dictionary key
                        'stack': player['stack'],
                    }
                }
            )
            
            return redirect('waiting_room')  # Przekierowanie z powrotem do 'waiting_room'
        else:
            print("Form is not valid")  # Debugging
            print(form.errors)  # Debugging
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

    table = Table()
    print(table.__dict__)
    print(f"Before shift_dealer_btn(): {table.dealer_btn}")
    table.shift_dealer_btn()
    print(f"After shift_dealer_btn(): {table.dealer_btn}")

    round_state = {
        'seats': players,
        'community_card': ['AS'],
        'pot': {
            'main': {'amount': 100},
        },
        'next_player': 1,
        'dealer_btn': table.dealer_btn,
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
                'message': {}
            }
        )
        return redirect('start_game')
    
    return render(request, 'start_game.html', {
        'round_state': round_state,
        'players': players,
        'hole_card': hole_card,
    })




