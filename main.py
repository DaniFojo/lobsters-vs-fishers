import time
import json
import os
import requests
import random

from tqdm import trange
import speech2text
from google_speech import Speech


URL = 'http://ec2-54-201-70-206.us-west-2.compute.amazonaws.com:5000/'
MAX_CONNECTION_TIME = 6
DISCUSS_TIME = 6
JSON_FILE = 'players.json'
MESSAGES = {
    'wl': 'LOBSTERS WIN',
    'wf': 'FISHERMEN WIN',
    'tie': 'GAME TIED'
}
LANGUAGE = "en"
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
INITIAL_LIVES = 3


def subtract_one_life(players, n):
    players[n]['lives'] -= 1
    update_players(players)


def read(message):
    speech = Speech(message, LANGUAGE)
    print(message)
    sox_effects = ("speed", "1.")
    speech.play(sox_effects)


def event_increase_all_lives(players):
    for p in players:
        if not p['lives'] == 0:
            p['lives'] += 0
    update_players(players)


EVENTS = [{'method': event_increase_all_lives, 'message': "It's raining. Everybody +1 live!"}]


def clear():
    os.system('clear')


def initialize_players(players):
    random.shuffle(players)
    num_players = len(players)
    for player in players[:N_LOBSTERS[num_players]]:
        player['class'] = 'lobster'
        player['lives'] = INITIAL_LIVES
    for player in players[N_LOBSTERS[num_players]:]:
        player['class'] = 'fisherman'
        player['lives'] = INITIAL_LIVES
    random.shuffle(players)
    return players


def update_players(players):
    r = requests.put(URL + 'update_players', data={'players': json.dumps(players)})
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
read('Welcome to Lobsters vs Fishermen')
print('='*40)
time.sleep(2)
clear()
read('Should we start the game?')
while True:
    transcript = speech2text.get_transcript_from_microphone()
    if True or speech2text.start_game(transcript):
        break
clear()
read('Start the game in your phones now')
while True:
    wait_bar(MAX_CONNECTION_TIME)
    players = read_players()
    if players and len(players) >= MAX_PLAYERS:
        read('Too many players!!')
        read('Resetting users...')
        clean_players()
    if players and len(players) >= MIN_PLAYERS:
        break
    else:
        read('Too few players!!')

num_players = len(players)
players = initialize_players(players)

update_players(players)

clear()
read('Starting game with {} players'.format(len(players)))
time.sleep(2)

while not game_finished(players):
    clear()
    read('A new day starts')
    time.sleep(2)
    read('You can now discuss for {} seconds'.format(DISCUSS_TIME))
    wait_bar(DISCUSS_TIME)
    clear()
    current_event = random.choice(EVENTS)
    read(current_event['message'])
    current_event['method'](players)
    time.sleep(2)
    clear()
    read("Now you can discuss for {} seconds".format(DISCUSS_TIME))
    wait_bar(DISCUSS_TIME)
    read("It's fishing time! Which player should be killed?")
    for i, p in enumerate(players):
        if p['lives'] > 0:
            print('{}: {}'.format(i+1, p['user']))
    confirmed = False
    while not confirmed:
        transcript = speech2text.get_transcript_from_microphone()
        if not transcript:
            continue
        target = speech2text.target_player(transcript, num_players)
        if not target:
            continue
        else:
            target -= 1
        read('Do you want to attack player number {}?'.format(target+1))
        transcript = speech2text.get_transcript_from_microphone()
        confirmed = speech2text.confirmation(transcript)
    subtract_one_life(players, target)
    read('Player number {} loses one life'.format(target+1))
    if players[target]['lives'] == 0:
        read('Player number {} died!'.format(target+1))
        read('Player number {} was a...'.format(target+1))
        time.sleep(2)
        read(players[target]['class'])
    else:
        read('Player number {} has {} lives left'.format(target + 1, players[target]['lives']))

print(MESSAGES[game_finished(players)])
