import json
import os
import requests
from flask import Flask
from flask import request, jsonify
from flask_cors import cross_origin, CORS
from ner import *
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ARRIA_HALF_TIME_URL = os.getenv("ARRIA_HALF_TIME_URL")
ARRIA_HALF_TIME_API_KEY = os.getenv("ARRIA_HALF_TIME_API_KEY")

ARRIA_LIVE_EVENTS_URL = os.getenv("ARRIA_LIVE_EVENTS_URL")
ARRIA_LIVE_EVENTS_API_KEY = os.getenv("ARRIA_LIVE_EVENTS_API_KEY")

ARRIA_PLAYERS_STATS_URL = os.getenv('ARRIA_PLAYERS_STATS_URL')
ARRIA_PLAYERS_STATS_API_KEY = os.getenv("ARRIA_PLAYERS_STATS_API_KEY")

RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")
RAPID_API_URL = os.getenv("RAPID_API_URL")
RAPID_API_VERSION = "v3"

@app.route("/api/query", methods=['POST'])
@cross_origin()
def query():
    data = request.json
    response = handle_user_query(data)
    return jsonify({"data": response})

# String processing for the user query.
def handle_user_query(query):
    # Here we should check the teams names against a knowledge base in case
    # we could find the word live in the query
    if 'live' in query:
        team_names = get_teams(query)
        api_response_first_team = search_team_by_name(team_names[0])
        id_first_team = json.loads(api_response_first_team)['response'][0]['team']['id']
        api_response_second_team = search_team_by_name(team_names[1])
        id_second_team = json.loads(api_response_second_team)['response'][0]['team']['id']

        api_response = get_fixture_by_team_ids(id_first_team, id_second_team)
        json_api_response = json.loads(api_response);
        events = json_api_response['response'][0]['events']
        json_api_response['response'] = events
        arria_response = get_arria_nlg_model(json.dumps(json_api_response), ARRIA_LIVE_EVENTS_URL, ARRIA_LIVE_EVENTS_API_KEY)

        response = json.loads(api_response)['response'][0]['events']
        for i in range(len(response) - 1):
            response[i]['nlg_model'] = arria_response.split('|')[i]

        return {'event_type': 'live', 'nlg_model': arria_response,'api_response': response}

    if 'half time' in query:
        team_names = get_teams(query)

        # Request team 1 info from RapiAPI
        api_response_first_team = search_team_by_name(team_names[0])
        id_first_team = json.loads(api_response_first_team)['response'][0]['team']['id']

        # Request team 2 info from RapiAPI
        api_response_second_team = search_team_by_name(team_names[1])
        id_second_team = json.loads(api_response_second_team)['response'][0]['team']['id']

        # Request match statistics for both teams head-to-head
        api_response = get_fixture_by_team_ids(id_first_team, id_second_team)
        value = json.loads(api_response)
        arria_response = get_arria_nlg_model(api_response, ARRIA_HALF_TIME_URL, ARRIA_HALF_TIME_API_KEY)

        return {'event_type':'half-time', 'nlg_model':arria_response, 'api_response' : json.loads(api_response)['response'][0]}
    if 'result' in query:
        api_response = get_full_time_stats('barcelona', 'a.c milan')
    if 'player' or 'players' in query:
        team_names = get_teams(query)

        # Request team 1 info from RapidAPI
        api_response_first_team = search_team_by_name(team_names[0])
        id_first_team = json.loads(api_response_first_team)['response'][0]['team']['id']

        # Request team 2 info from RapidAPI
        api_response_second_team = search_team_by_name(team_names[1])
        id_second_team = json.loads(api_response_second_team)['response'][0]['team']['id']

        # Request match statistics for both teams head-to-head
        api_response = get_fixture_by_team_ids(id_first_team, id_second_team)
        value = {'players' : json.loads(api_response)['response'][0]['players']}
        arria_response = get_arria_nlg_model(json.dumps(value), ARRIA_PLAYERS_STATS_URL, ARRIA_PLAYERS_STATS_API_KEY)
        formation_string = arria_response.split('||')[0]
        players_string = arria_response.split('||')[1].split('--')
        return {'event_type': 'players-statistics', 'nlg_model': players_string,
                'api_response': json.loads(api_response)['response'][0]}


def get_teams(text):
    club_names = extract_club_names(text)
    if len(club_names) == 2:
        return club_names
    if len(club_names) == 3:
        return [f'{club_names[0]} {club_names[1]}', {club_names[2]}]
    return

def get_player_names(text):
    extract_player_names(text)

def get_fixture_by_team_ids(team_a, team_b):
    querystring = {"h2h": f'{team_a}-{team_b}'}
    response = get_rapid_api_data(
        f'{RAPID_API_URL}/{RAPID_API_VERSION}/fixtures/headtohead',
        querystring)
    querystring = {"id": json.loads(response.text)['response'][0]['fixture']['id']}
    response = get_rapid_api_data(
        f'{RAPID_API_URL}/{RAPID_API_VERSION}/fixtures',
        querystring)
    return response.text


def get_full_time_stats(team_a, team_b):
    pass


def get_player_stats(team_a, team_b):
    pass


def search_team_by_name(team):
    querystring = {"search": team }
    response = get_rapid_api_data(
        f'{RAPID_API_URL}/{RAPID_API_VERSION}/teams',
        querystring)
    return response.text

def get_rapid_api_data(url, query_string):
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }

    return requests.request("GET", url, headers=headers, params=query_string)


def get_arria_nlg_model(data, url, api_key):
    # Define headers and parameters for API request
    headers = {'Authorization': 'Bearer ' + api_key}
    params = {'output': 'json'}

    data = json.loads(data)
    # Send API request
    response = requests.post(url, headers=headers, json={"data":[{"id":"Primary","type":"json","jsonData":data}]}, params=params)

    # Check response status code and content
    if response.status_code == 200:
        output_data = response.json()
        return output_data[0]['result'].replace('<p>', '').replace('</p>', '')
    else:
        print('Error:', response.status_code, response.text)


if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5001)
