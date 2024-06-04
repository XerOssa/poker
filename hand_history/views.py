from django.shortcuts import render, redirect
import pandas as pd
import matplotlib.pyplot as plt
from poker_analysis import process_poker_hand, save_to_csv
from .models import Player
import os
from django.conf import settings
import waiting_room_param 
from forms import PlayerForm


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
    
    config = configurations_table
    config['small_blind'] *= 2

    config_form = GameConfigForm(initial=config)

    players = players_list
    if request.method == 'POST':
        config_form = GameConfigForm(request.POST)
        form = PlayerForm(request.POST)
        if config_form.is_valid():
            config = config_form.cleaned_data
        if form.is_valid():
            player = form.save()
            # Recalculate display_id
            display_id = len(Player.objects.all()) + 1
            players.append({'id': display_id, 'type': 'Hero', 'name': player.name})
            return redirect('waiting_room')
        else:
            print("Form is not valid")  # Debugging
            print(form.errors)  # Debugging
    else:
        form = PlayerForm() 


    return render(request, 'waiting_room.html', {
        'config': config,
        'form': form,
        'players': players,
        'config_form': config_form,
    })


def start_game_view(request):
    # Pobranie listy graczy z sesji
    players = request.session.get('players', [])

    return render(request, 'start_game.html', {
        'players': players,
        'round_state': {
            'round_count': 1,
            'street': 'flop',
            'seats': players,
            'community_card': ['AS'],
            'pot': {
                'main': {'amount': 500},
                'side': [{'amount': 200}, {'amount': 300}]
            }
        }
    })
