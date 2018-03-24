import json
import os
import random
from flask import Flask, session, redirect, url_for, escape, request
app = Flask(__name__)

players_filename = 'files/players.json'
player_status_filename = 'files/player_status.json'
round_ended = False

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Welcome!'


@app.route('/new_player', methods=['GET', 'POST'])
def new_player():
    _new_player = dict()
    _new_player['lives'] = -1
    _new_player['class'] = ''
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


@app.route('/increase_life_to_player', methods=['PUT'])
def increase_life_to_player():
    global players
    user = request.form['user']
    for i in range(len(players)):
        if players[i]['user'] == user:
            players[i]['lives'] += 1
    return '200'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)