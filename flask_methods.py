import json
import os
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
    form = request.form
    player = dict()
    player['user_name'] = form['user']
    player['player_ip'] = request.remote_addr

    with open(players_filename, 'a') as players_file:
        players_file.write(json.dumps(player))
        players_file.write('\n')
    return '200'


@app.route('/clean_players', methods=['DELETE'])
def clean_players():
    round_ended = True
    if os.path.isfile(players_filename):
        os.remove(players_filename)
    return '200'


@app.route('/get_players', methods=['GET'])
def get_players():
    if not os.path.isfile(players_filename):
        return json.dumps([])
    else:
        players = []
        with open(players_filename, 'r') as players_file:
            for line in players_file.readlines():
                players.append(json.loads(line))

        return json.dumps(players)

@app.route('/update_players', methods=['UPDATE'])
def update_players():
    if not os.path.isfile():



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



