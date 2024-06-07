from django.shortcuts import render, redirect
import pandas as pd
import matplotlib.pyplot as plt
from poker_analysis import process_poker_hand, save_to_csv
from .models import Player
import os
from django.conf import settings
from waiting_room_param import players_list, configurations_table, read_config
from .forms import PlayerForm, GameConfigForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def home(request):
    context = {}
    Player.objects.all().delete()
    return render(request, 'home.html', context)


def handhistory(request):
    FILES_PATH = 'D:/ROBOTA/python/poker/hh/*.txt'
    hands = process_poker_hand(FILES_PATH)
    poker_hands = []
    for hand_data in hands:
        poker_hands.append(hand_data)

    return render(request, 'handhistory.html', {'poker_hands': poker_hands})


def charts(request):
    FILES_PATH = 'D:/ROBOTA/python/poker/hh/*.txt'
    hands = process_poker_hand(FILES_PATH)

    save_to_csv(hands)
    df = pd.read_csv('D:/ROBOTA/python/poker/poker_hand.csv')
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

    file_path = 'D:/ROBOTA/python/poker/hand_history/config_players.txt'
    config_players = read_config(file_path)
    players = players_list(config_players)

    if request.method == 'POST':
        config_form = GameConfigForm(request.POST)
        form = PlayerForm(request.POST)
        if config_form.is_valid():
            config_table = config_form.cleaned_data
        if form.is_valid():
            player = form.save()
            channel_layer = get_channel_layer()
            display_id = len(Player.objects.all()) + 1
            players.append({'id': display_id, 'type': 'Hero', 'name': player.name})

            # Zapisz listę graczy w sesji
            request.session['players'] = players
            async_to_sync(channel_layer.group_send)(
                'poker', {
                    'type': 'register_player',
                    'message': {
                        'name': player.name
                    }
                }
            )
            
            return redirect('waiting_room')  # Przekierowanie z powrotem do 'waiting_room'
        else:
            print("Form is not valid")  # Debugging
            print(form.errors)  # Debugging
    else:
        form = PlayerForm()

    return render(request, 'waiting_room.html', {
        'config': config_table,
        'form': form,
        'players': players,
        'config_form': config_form,
    })


def start_game_view(request):
    players = request.session.get('players', [])

    round_state = {
        'round_count': 1,
        'street': 'flop',
        'seats': players,
        'community_card': ['AS'],
        'pot': {
            'main': {'amount': 100},
            'side': [{'amount': 200}, {'amount': 300}]
        },
        'next_player': 1,  # index of the next player
        'dealer_btn': 0,
        'small_blind_pos': 1,
        'big_blind_pos': 2
    }
    half_length = len(round_state['seats']) // 2
    upper_seats = round_state['seats'][:half_length]
    lower_seats = round_state['seats'][half_length:]
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
        'upper_seats': upper_seats,
        'lower_seats': lower_seats,
    })


