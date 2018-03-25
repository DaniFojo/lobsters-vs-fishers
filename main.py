import json
import os
import sys
import random
import time
import requests
from termcolor import cprint
from tqdm import trange
from google_speech import Speech

import speech2text
import os

rows, columns = os.popen('stty size', 'r').read().split()
rows = int(rows)
columns = int(columns)
URL = 'http://ec2-54-201-70-206.us-west-2.compute.amazonaws.com:5000/'
MAX_CONNECTION_TIME = 60
DISCUSS_TIME = 60
JSON_FILE = 'players.json'
MESSAGES = {
    'wl': 'LOBSTERS WIN',
    'wf': 'FISHERS WIN',
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


def check_if_dead(players, user):
    for p in players:
        if p['user'] == user and p['is_alive'] == 'yes':
            if p['lives'] <= 0:
                p['lives'] = 0
                p['is_alive'] = 'no'
                read('Player {} died!'.format(user))
    update_players(players)


def subtract_one_life(players, n):
    players[n]['lives'] -= 1
    read('Player number {} loses one life'.format(n+1))
    check_if_dead(players, players[n]['user'])
    update_players(players)


def read(message, print_text=True):
    speech = Speech(message, LANGUAGE)
    if print_text:
        cprint('\n'*(rows//2) + ' '*((columns//2)-(len(message)//2)) + message, 'red', attrs=['bold'])
    sox_effects = ("speed", "1.")
    speech.play(sox_effects)


def event_increase_all_lives(players):
    for p in players:
        if p['is_alive'] == 'yes':
            p['lives'] += 1
            p['to_update'] = 'yes'
    update_players(players)


def event_two_lives_lost(players):
    while True:
        doomed_index = random.randint(1, len(players)-1)
        if players[doomed_index]['is_alive'] == 'yes':
            break
    players[doomed_index]['lives'] = max(0, players[doomed_index]['lives']-2)
    read('Player {} has now {} lives.'.format(players[doomed_index]['user'],
                                              players[doomed_index]['lives']))
    check_if_dead(players, players[doomed_index]['user'])
    for p in players:
        p['to_update'] = 'yes'
    update_players(players)


def event_choose_with_whom_to_switch_classes(players):
    while True:
        who_chooses = random.choice(players)['user']
        if who_chooses['is_alive'] == 'yes':
            break
    for player in players:
        player['to_update'] = 'yes'
        if player['user'] == who_chooses:
            player['can_choose'] = 'yes'
    update_players(players)
    while True:
        time.sleep(0.5)
        r = requests.get(URL + 'has_been_chosen')
        if r.text:
            the_chosen = r.text
            break
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] in (who_chooses, the_chosen):
            players[i]['class'] = 'fisherman' if players[i]['class'] == 'lobster' else 'lobster'
    update_players(players)


def event_choose_who_to_attack(players):
    while True:
        who_chooses = random.choice(players)['user']
        if who_chooses['is_alive'] == 'yes':
            break
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] == who_chooses:
            players[i]['can_choose'] = 'yes'
    update_players(players)
    while True:
        time.sleep(1)
        r = requests.get(URL + 'has_been_chosen')
        if r.text:
            the_chosen = r.text
            break
    for i in range(len(players)):
        players[i]['to_update'] = 'yes'
        if players[i]['user'] == the_chosen:
            players[i]['lives'] -= 1
            read('Player {} has now {} lives.'.format(the_chosen, players[i]['lives']))
            check_if_dead(players, the_chosen)
    update_players(players)


def event_steal_a_live(players):
    who_chooses = random.choice([p for p in players if p['is_alive'] == 'yes'])
    for player in players:
        player['to_update'] = 'yes'
        if player['user'] == who_chooses:
            player['can_choose'] = 'yes'
    update_players(players)
    the_chosen = None
    while not the_chosen:
        time.sleep(1)
        r = requests.get(URL + 'has_been_chosen')
        the_chosen = r.text
    for player in players:
        player['to_update'] = 'yes'
        if player['user'] == the_chosen:
            player['lives'] -= 1
            read('Player {} has now {} lives.'.format(the_chosen, player['lives']))
        elif player['user'] == who_chooses:
            player['lives'] += 1
            read('Player {} has now {} lives.'.format(who_chooses, player['lives']))
    update_players(players)


EVENTS = [{'method': event_steal_a_live,
           'message': "It's windy! Someone gets to steal a life."},
          {'method': event_increase_all_lives,
           'message': "It's sunny! Everybody +1 live!"},
          {'method': event_two_lives_lost,
           'message': "A lightning bolt struck! Someone loses 2 lives!"},
          {'method': event_choose_who_to_attack,
           'message': "It's raining! One player chooses a second one, who looses one life."},
          {'method': event_choose_with_whom_to_switch_classes,
           'message': "There is full moon! Two players switch classes."}]


def clear():
    os.system('clear')


def initialize_players(players):
    random.shuffle(players)
    num_players = len(players)
    for player in players[:N_LOBSTERS[num_players]]:
        player['class'] = 'lobster'
        player['lives'] = INITIAL_LIVES
        player['is_alive'] = 'yes'
    for player in players[N_LOBSTERS[num_players]:]:
        player['class'] = 'fisherman'
        player['lives'] = INITIAL_LIVES
        player['is_alive'] = 'yes'
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
    for _ in trange(t):
        time.sleep(1.)


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
tmp = len("|______\___/|_.__/|___/\__\___|_|  |___/   \_/ |___/ |_|    |_|___/_| |_|\___|_|  |___/")
cprint(
' '*(columns//2-tmp//2) + " _           _         _                              ______ _     _                   \n"+
' '*(columns//2-tmp//2) + "| |         | |       | |                            |  ____(_)   | |                  \n"+
' '*(columns//2-tmp//2) + "| |     ___ | |__  ___| |_ ___ _ __ ___  __   _____  | |__   _ ___| |__   ___ _ __ ___ \n"+
' '*(columns//2-tmp//2) + "| |    / _ \| '_ \/ __| __/ _ \ '__/ __| \ \ / / __| |  __| | / __| '_ \ / _ \ '__/ __|\n"+
' '*(columns//2-tmp//2) + "| |___| (_) | |_) \__ \ ||  __/ |  \__ \  \ V /\__ \ | |    | \__ \ | | |  __/ |  \__ \\\n"+
' '*(columns//2-tmp//2) + "|______\___/|_.__/|___/\__\___|_|  |___/   \_/ |___/ |_|    |_|___/_| |_|\___|_|  |___/\n", 'red')
read('Welcome to Lobsters vs Fishers.', print_text=False)
time.sleep(.2)
clear()
read("I am the MASTER LOBSTER.")
time.sleep(.2)
clear()
read("I will be your narrator for this adventure.")
time.sleep(.2)
clear()
read("Today, you are fortuned.")
time.sleep(.2)
clear()
read("You will take the roles of valiant FISHERS who had the "
     "courage to try to fish the deadly LOBSTERS.")
time.sleep(.2)
clear()
read("Who will be victorious? Only you can decide the fate of this battle.")
clear()
read('Should we start the game?')
while True:
    transcript = speech2text.get_transcript_from_microphone()
    if speech2text.start_game(transcript):
        break
clear()
read('Start the game in your phones now.')
attempts = 3
while attempts:
    wait_bar(MAX_CONNECTION_TIME)
    players = read_players()
    if players and len(players) >= MAX_PLAYERS:
        read('Too many players!!')
        read('Resetting users...')
        clean_players()
        clear()
    elif players and len(players) >= MIN_PLAYERS:
        break
    else:
        read('Too few players!!')
        if attempts > 1:
            read('Waiting {} seconds more'.format(MAX_CONNECTION_TIME))
    attempts -= 1
if attempts == 0:
    read('The fate of this battle will remain undecided.')
    read('Until next time!')
    sys.exit(0)


num_players = len(players)
players = initialize_players(players)

update_players(players)

clear()
read('Starting game with {} players.'.format(num_players))
clear()
read('Today, {} deadly Lobsters will fight against {} valiant Fishers.'.format(N_LOBSTERS[num_players],
                                                                                num_players-N_LOBSTERS[num_players]))
clear()
read('Look at your devices to see your role.')
time.sleep(2)

while not game_finished(players):
    clear()
    read('A new day starts.')
    time.sleep(2)
    clear()
    read('You can now discuss for {} seconds.'.format(DISCUSS_TIME))
    wait_bar(DISCUSS_TIME)
    clear()
    current_event = random.choice(EVENTS)
    read(current_event['message'])
    current_event['method'](players)
    clear()
    read("Now you can discuss for {} seconds.".format(DISCUSS_TIME))
    wait_bar(DISCUSS_TIME)
    confirmed = False
    while not confirmed:
        clear()
        read("It's fishing time! Which player should be killed?")
        colors = {
            0: 'blue',
            1: 'cyan',
            2: 'green',
            3: 'yellow',
            4: 'red',
            5: 'magenta',
            6: 'blue',
            7: 'cyan',
            8: 'green',
            9: 'yellow'
        }
        for i, p in enumerate(players):
            if p['lives'] > 0:
                cprint(('{}: {}'.format(i + 1, p['user'])), color=colors[i])
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
        if not confirmed:
            read('Ok, cancelling...'.format(target+1))
    subtract_one_life(players, target)
    if players[target]['lives'] == 0:
        read('Player number {} was a...'.format(target+1))
        time.sleep(2)
        read(players[target]['class'])
    else:
        read('Player number {} has {} lives left.'.format(target + 1, players[target]['lives']))

read('The game has ended!')
time.sleep(0.3)
read(MESSAGES[game_finished(players)])
read('Thank you for playing!')
read('Until next time!')
