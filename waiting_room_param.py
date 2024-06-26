import ast
from django import forms
from hand_history.models import Player



def read_config(file_path):
    config_players = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Ignore empty lines
                player_info = ast.literal_eval("{" + line.strip() + "}")
                config_players.append({'name': player_info['name'], 'path': player_info['path'], 'type': 'AI'})
    return config_players


file_path = 'D:/ROBOTA/python/poker/hand_history/config_players.txt'


def configurations_table(config_table):
    config_table = {
            'initial_stack': 100,
            'small_blind': 5,
            'ante': 0,
        }
    return config_table    


def players_list(config_players):
    players = []
    for idx, player_info in enumerate(config_players, start=0):
        players.append({'idx': idx, 'type': player_info['type'], 'name': player_info['name'], 'path': player_info['path']})

    # Add players from the database to the players list with sequential display_id
    db_players = Player.objects.all()
    for idx, player in enumerate(db_players, start=len(config_players)):
        players.append({'idx': idx, 'type': 'Hero', 'name': player.name, 'stack': player.stack})
    return players

