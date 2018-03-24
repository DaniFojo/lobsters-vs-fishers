import json
import os
from flask import Flask, session, redirect, url_for, escape, request
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Welcome!'


@app.route('/new_player', methods=['POST'])
def new_player():
    form = request.form
    player = dict()
    player['user_name'] = form['user']
    player['player_ip'] = request.remote_addr
    with open('players.json', 'a') as players_file:
        print(json.dumps(player))
        players_file.write(json.dumps(player))
        players_file.write('\n')
    return '200'


@app.route('/clean_players', methods=['POST'])
def clean_players():
    os.remove('players.json')
    return '200'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



