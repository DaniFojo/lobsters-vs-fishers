import json
import os
from flask import Flask, session, redirect, url_for, escape, request
app = Flask(__name__)

players_filename = 'files/players.json'
player_status_filename = 'files/player_status.json'
round_ended = False

# Constants
NO = 'no'
YES = 'yes'

# Global variables
players = list()
chosen_user = ''
pause = NO


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Welcome!'


@app.route('/new_player', methods=['GET', 'POST'])
def new_player():
    _new_player = dict()
    _new_player['lives'] = -1
    _new_player['class'] = ''
    _new_player['can_choose'] = NO
    _new_player['to_update'] = NO
    _new_player['user'] = request.form['user']
    global players
    players.append(_new_player)
    return '200'


@app.route('/clean_players', methods=['DELETE'])
def clean_players():
    global players
    players = list()
    return '200'


@app.route('/get_players', methods=['GET'])
def get_players():
    return json.dumps(players)


@app.route('/update_players', methods=['PUT'])
def update_players():
    global players
    players = json.loads(request.form['players'])
    return '200'


@app.route('/to_update', methods=['POST'])
def to_update():
    return str([p for p in players if p['user'] == request.form['user']][0]['to_update'])


@app.route('/update_in_client', methods=['POST'])
def update_in_client():
    user = request.form['user']
    to_return = ''
    global players
    for i in range(len(players)):
        if players[i]['user'] == user:
            players[i]['to_update'] = NO
            to_return = json.dumps(players[i])
    return to_return


@app.route('/my_choice_is', methods=['POST'])
def my_choice_is():
    user = request.form['user']
    global players
    for i in range(len(players)):
        if players[i]['user'] == user:
            players[i]['can_choose'] = NO
            global chosen_user
            chosen_user = request.form['choice']
    return '200'


@app.route('/has_been_chosen', methods=['GET'])
def has_been_chosen():
    global chosen_user
    to_return = chosen_user
    chosen_user = ''
    return to_return


@app.route('/is_paused', methods=['GET'])
def is_paused():
    return pause


@app.route('/toggle_pause', methods=['PUSH'])
def toggle_pause():
    global pause
    pause = NO if pause == YES else YES
    return '200'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



