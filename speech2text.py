#!/usr/bin/env python3

import speech_recognition as sr

with open('credentials.json', 'r') as f:
    CREDENTIALS = f.read()


def get_transcript_from_microphone(max_time=5, service='google_cloud'):
    """
    Transcrives audio gotten from the microphone.
    :param max_time:
    :param service:
    :return:
    """
    recognizer = sr.Recognizer()
    if service == 'google_cloud':
        while True:
            with sr.Microphone() as source:
                print('Listening...')
                audio = recognizer.listen(source, phrase_time_limit=max_time)
            try:
                transcript = recognizer.recognize_google_cloud(audio, credentials_json=CREDENTIALS)
                return transcript
            except sr.UnknownValueError:
                print("Could not understand audio, try again")
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
