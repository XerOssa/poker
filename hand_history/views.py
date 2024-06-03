from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PlayerForm
import pandas as pd
import matplotlib.pyplot as plt
from poker_analysis import process_poker_hand, save_to_csv
from .models import Player
import os
import ast
from django.conf import settings
from django import forms

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


class GameConfigForm(forms.Form):
    initial_stack = forms.IntegerField(label='Initial Stack', initial=100, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))
    small_blind = forms.IntegerField(label='Small Blind', initial=5, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))
    ante = forms.IntegerField(label='Ante', initial=0, widget=forms.TextInput(attrs={'style': 'text-align: center;'}))


def read_config(file_path):
    config_players = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Ignore empty lines
                player_info = ast.literal_eval("{" + line.strip() + "}")
                config_players.append({'name': player_info['name'], 'path': player_info['path'], 'type': 'AI'})
    return config_players

file_path = 'D:/ROBOTA/python/poker/hand_history/config_players.txt'
config_players = read_config(file_path)


def waiting_room_view(request):
    config = {
        'initial_stack': 100,
        'small_blind': 5,
        'ante': 0,
    }

    config['small_blind'] *= 2

    players = []  # Initialize players as a list
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
        config_form = GameConfigForm(initial=config)
        form = PlayerForm()  # Initialize the form when the request is not "POST"

    # Add AI players from config_players to the players list
    for idx, player_info in enumerate(config_players, start=1):
        players.append({'id': idx, 'type': player_info['type'], 'name': player_info['name'], 'path': player_info['path']})

    # Add players from the database to the players list with sequential display_id
    db_players = Player.objects.all()
    for idx, player in enumerate(db_players, start=len(config_players) + 1):
        players.append({'id': idx, 'type': 'Hero', 'name': player.name})


    return render(request, 'waiting_room.html', {
        'rules': config,
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
