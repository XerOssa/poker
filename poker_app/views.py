import matplotlib.pyplot as plt
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from poker_analysis import process_poker_hand, save_to_csv
from .models import Hero
from waiting_room_param import players_list, read_config
from .forms import HeroForm, GameConfigForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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


def my_view(request):
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    suits = ["s", "d", "h", "c"]

    return render(request, 'index.html', {
        'ranks': ranks,
        'suits': suits,
    })


def waiting_room_view(request):
    
    form_config_table_data = {}
    file_path = 'poker_app/config_players.txt'
    config_players = read_config(file_path)
    players = players_list(config_players)

    if request.method == 'POST':
        # request.session.clear()
        
        form_config_table = GameConfigForm(request.POST)
        form = HeroForm(request.POST)               

        if form_config_table.is_valid():
            config_data = form_config_table.cleaned_data
            form_config_table_data = {
                'initial_stack': config_data.get('initial_stack'),
                'small_blind': config_data.get('small_blind'),
                'ante': config_data.get('ante'),
            }
            request.session['form_config_table'] = form_config_table_data

            game_config = {
                'initial_stack': form_config_table_data.get('initial_stack'),
                'small_blind': form_config_table_data.get('small_blind'),
                'ante': form_config_table_data.get('ante'),
                'ai_players': players
            }
            request.session['game_config'] = game_config
            return redirect('waiting_room')

        if form.is_valid():
            hero = form.save(commit=False)
            hero.save()
            initial_stack = request.session['game_config'].get('initial_stack', 100)

            display_id = len(players)
            players.append({
                'idx': display_id,
                'type': 'human',
                'name': hero.name,
            })
            for player in players:
                player['stack'] = initial_stack

            request.session['players'] = players
            request.session['hero'] = {'name': hero.name}
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
        print(form.errors)
        print(form_config_table.errors)
    else:
        form = HeroForm()

        # Wypełnij formularz danymi z sesji, jeśli istnieją
        if 'form_config_table' in request.session:
            form_config_table = GameConfigForm(initial=request.session['form_config_table'])
        else:
            form_config_table = GameConfigForm() 

    return render(request, 'waiting_room.html', {
        'form': form,
        'form_config_table': form_config_table,
        'players': players,
    })






def start_game_view(request):
    players = request.session.get('players', [])
    return render(request, 'start_game.html', {
        'players': players,
    })

