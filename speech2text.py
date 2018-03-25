#!/usr/bin/env python3

import os

import speech_recognition as sr
from termcolor import cprint

rows, columns = os.popen('stty size', 'r').read().split()
rows = int(rows)
columns = int(columns)


with open('credentials.json', 'r') as f:
    CREDENTIALS = f.read()


def get_transcript_from_microphone(max_time=5, service='google_cloud'):
    """
    Transcribes audio gotten from the microphone.
    :param max_time:
    :param service:
    :return:
    """
    recognizer = sr.Recognizer()
    if service == 'google_cloud':
        while True:
            with sr.Microphone() as source:
                cprint('\n' + ' ' * ((columns // 2) - (len("Listening...") // 2)) + "Listening...", 'magenta',
                       attrs=['bold'])
                audio = recognizer.listen(source, phrase_time_limit=max_time)
            try:
                transcript = recognizer.recognize_google_cloud(audio, credentials_json=CREDENTIALS)
                return transcript
            except sr.UnknownValueError:
                cprint('\n' + ' ' * ((columns // 2) - (len("I couldn't understand what you said, try again please.") // 2)) + "I couldn't understand what you said, try again please.", 'magenta',
                       attrs=['bold'])
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {}".format(e))

    else:
        raise NotImplementedError


def target_player(transcript, num_players):
    """
    Given a transcript returns who is the target player.
    :param transcript:
    :param num_players:
    :return:
    """
    target = None
    numbers = {str(i) for i in range(1, num_players+1)}
    for word in transcript.split():
        if word in numbers:
            if not target:
                target = int(word)
            else:
                print('Could not get player from speech.')
    return target


def start_game(transcript):
    """
    Given a transcripts returns if the game should start.
    :param transcript:
    :return:
    """
    transcript = transcript
    keywords = {'start', 'begin', 'commence', 'go', 'start.', 'begin.', 'commence.', 'go.', 'yes', 'yes.'}
    for word in transcript.split():
        if word.lower() in keywords:
            return True
    return False


def confirmation(transcript):
    """
    Given a transcripts returns if the game should start.
    :param transcript:
    :return:
    """
    transcript = transcript
    keywords = {'ok', 'okay', 'yes', 'go', 'ok.', 'okay.', 'yes.'}
    for word in transcript.split():
        if word.lower() in keywords:
            return True
    return False
