import time
import json
import os
import requests
import random

from tqdm import trange
import speech2text


URL = 'http://ec2-54-201-70-206.us-west-2.compute.amazonaws.com:5000/'
MAX_CONNECTION_TIME = 6
DISCUSS_TIME = 60
JSON_FILE = 'players.json'
MESSAGES = {
    'wl': 'LOBSTERS WIN',
    'wf': 'FISHERMEN WIN',
    'tie': 'GAME TIED'
}
MIN_PLAYERS = 5
MAX_PLAYERS = 10
N_LOBSTERS = {
    5: 2,
    6: 2,
    7: 3,
    8: 3,
    9: 4,
    10: 4
}


def event_increase_all_lives(players):
    for p in players:
        if not p['lives'] == 0:
            p['lives'] += 1
            p['to_update'] = 'yes'
    update_players(players)

def event_player_steal_life(players):


def event_choose_with_whom_to_switch_classes(players):
    who_chooses = random.choice(players)['user']
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] == who_chooses:
            players[i]['can_choose'] = 'yes'
    update_players(players)
    print('Two players will switch classes')
    while True:
        the_chosen = requests.get(URL + 'has_been_chosen')
        if the_chosen:
            break
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] in (who_chooses, the_chosen):

            players[i]['class'] = 'fisherman' if players[i]['class'] == 'lobster' else 'lobster'


def event_choose_who_to_attack(players):
    who_chooses = random.choice(players)['user']
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] == who_chooses:
            players[i]['can_choose'] = 'yes'
    update_players(players)
    print('One player chooses a second one, the latter looses one life.')
    while True:
        the_chosen = requests.get(URL + 'has_been_chosen')
        if the_chosen:
            break
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] == the_chosen:
            players[i]['lives'] -= 1


EVENTS = [{'method': event_increase_all_lives, 'message': "It's raining. Everybody +1 live!"}]



def clear():
    os.system('clear')


def initialize_players(players):
    random.shuffle(players)
    num_players = len(players)
    for player in players[:N_LOBSTERS[num_players]]:
        player['class'] = 'lobster'
        player['lives'] = 3
    for player in players[N_LOBSTERS[num_players]:]:
        player['class'] = 'fisherman'
        player['lives'] = 3
    return players


def update_players(players):
    print(json.dumps(players))
    r = requests.post(URL + 'update_players', data={'players': json.dumps(players)})
    if not r.status_code == 200:
        raise Exception


def read_players():
    r = requests.get(URL + 'get_players')
    if not r.status_code == 200:
        raise Exception
    players = json.loads(r.text)
    return players


def clean_players():
    r = requests.delete(URL + 'clean_players')
    if not r.status_code == 200:
        raise Exception


def wait_bar(t):
    for _ in trange(t*10):
        time.sleep(.1)


def game_finished(players):
    lobsters = [l for l in players if l['class'] == 'lobster']
    fishermen = [f for f in players if f['class'] == 'fisherman']
    total_lives_lobsters = sum([i['lives'] for i in lobsters])
    total_lives_fishermen = sum([i['lives'] for i in fishermen])
    if total_lives_lobsters + total_lives_fishermen == 0:
        return 'tie'
    elif total_lives_lobsters == 0:
        return 'wf'
    elif total_lives_fishermen == 0:
        return 'wl'
    return False


clean_players()

clear()
print('Welcome to Lobsters vs Fishermen')
print('='*40)
time.sleep(4)
clear()
print('Should we start the game?')
while True:
    transcript = speech2text.get_transcript_from_microphone()
    if True or speech2text.start_game(transcript):
        break
clear()
print('Start the game in your phones now')
while True:
    wait_bar(MAX_CONNECTION_TIME)
    players = read_players()
    if players and len(players) >= MAX_PLAYERS:
        print('Too many players!! :(')
        print('Resetting users...')
        clean_players()
    if players and len(players) >= MIN_PLAYERS:
        break
    else:
        print('Too few players!! :(')

players = initialize_players(players)

update_players(players)

clear()
print('Starting game with {} players'.format(len(players)))
time.sleep(2)

while not game_finished(players):
    print('A new day starts')
    time.sleep(2)
    print('You can now discuss for {} seconds'.format(DISCUSS_TIME))
    wait_bar(DISCUSS_TIME)
    clear()
    current_event = random.choice(EVENTS)
    print(current_event['message'])
    current_event['method'](players)
    time.sleep(2)
    clear()
    print("Now you can discuss for {} seconds".format(DISCUSS_TIME))
    wait_bar(DISCUSS_TIME)
    print("It's fishing time! Which player should be killed?")
    for i, p in enumerate(players):
        print('{}: {}'.format(i, p['user']))
    # TODO KILL 1 PLAYER


print(MESSAGES[game_finished(players)])
