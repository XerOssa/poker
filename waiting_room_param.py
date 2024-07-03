import ast
from django import forms
from poker_app.models import Hero


def read_config(file_path):
    file_path = 'poker_app/config_players.txt'
    config_players = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Ignore empty lines
                player_info = ast.literal_eval("{" + line.strip() + "}")
                config_players.append({'name': player_info['name'], 'path': player_info['path'], 'type': 'AI'})
    return config_players





def configurations_table(default_config_table):
    default_config_table = {
            'initial_stack': 150,
            'small_blind': 5,
            'ante': 0,
        }
    return default_config_table    


def players_list(config_players):
    players = []
    for idx, player_info in enumerate(config_players, start=0):
        players.append({'idx': idx, 'type': player_info['type'], 'name': player_info['name'], 'path': player_info['path']})

    # Add players from the database to the players list with sequential display_id
    db_players = Hero.objects.all()
    for idx, player in enumerate(db_players, start=len(config_players)):
        players.append({'idx': idx, 'type': 'Hero', 'name': player.name})

    return players