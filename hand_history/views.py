from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import PlayerForm
import pandas as pd
import matplotlib.pyplot as plt
from poker_analysis import process_poker_hand, save_to_csv
from .models import Player

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

    plot_path = 'static/charts/poker_hand.png'

    plt.savefig(plot_path)
    return render(request, 'charts.html', {'plot_path': plot_path})



def game_rule_view(request):
    config = {
        'initial_stack': 100,
        'small_blind': 5,
        'ante': 0,
    }

    config['small_blind'] *= 2

    # Definiowanie ai_players na początku, aby była dostępna w każdym przypadku
    ai_players = [
        {'type': 'AI', 'name': '0_fish_player', 'path': 'D:/ROBOTA/python/poker/hand_history/sample_player/fish_player_setupCHECK.py'},
        {'type': 'AI', 'name': '1_random_player', 'path': 'D:/ROBOTA/python/poker/hand_history/sample_player/random_player_setupCHECK.py'},
        {'type': 'AI', 'name': '2_Tag', 'path': 'D:/ROBOTA/python/poker/hand_history/sample_player/TagCHECK.py'},
        {'type': 'AI', 'name': '3_fish', 'path': 'D:/ROBOTA/python/poker/hand_history/sample_player/fish_player_setupCHECK.py'},
        {'type': 'AI', 'name': '4_Whale', 'path': 'D:/ROBOTA/python/poker/hand_history/sample_player/fish_player_setupCHECK.py'}
    ]

    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            # Dodanie nowego gracza do listy ai_players
            ai_players.append({'type': 'Hero', 'name': player.name})
            return redirect('waiting_room')
        else:
            print("Form is not valid")  # Debugowanie
            print(form.errors)  # Debugowanie
    else:
        form = PlayerForm()  # Inicjalizacja formularza w przypadku, gdy żądanie nie jest "POST"

    # Dodanie graczy z bazy danych do listy ai_players
    db_players = Player.objects.all()
    for player in db_players:
        ai_players.append({'type': 'Hero', 'name': player.name})

    # Debugowanie
    print("Liczba graczy w bazie danych:", db_players.count())
    for player in db_players:
        print("Gracz w bazie danych:", player.name, 'Hero')

    return render(request, 'waiting_room.html', {
        'rules': config,
        'form': form,
        'ai_players': ai_players
    })



def start_game_view(request):
    if request.method == 'POST':
        # Obsługa logiki rozpoczęcia gry
        return HttpResponse("Game started")
    return redirect('start_game.html')