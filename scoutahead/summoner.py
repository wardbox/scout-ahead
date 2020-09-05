from riotwatcher import LolWatcher, ApiError
from datetime import datetime
from scoutahead.db import *
from sqlalchemy import desc, asc
import json

def get_team(team):
    
    team = team.lower().split(',')
    if len(team) < 5:
        return None
    #    pass
    summoners = []

    for player in team:
        summoner = get_summoner(player)
        champions = get_best_champion(summoner)
        summoners.append(summoner)
    return summoners

def get_summoner(summoner_name):

    f = open("key.txt", "r")
    riot_key = f.read()
    watcher = LolWatcher(riot_key)
    region = 'na1'

    try:
        response = watcher.summoner.by_name(region, summoner_name)
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            return 'Summoner with that ridiculous name not found.'
        else:
            raise
        return err

    # Check if someone with this puuid already exists locally.
    if Summoner.query.filter_by(riotPuuid=response['puuid']).first() is not None:
        return Summoner.query.filter_by(riotPuuid=response['puuid']).first()

    else:
        new_summoner = Summoner(
            name = response['name'],
            profileIconId = response['profileIconId'],
            revisionDate = response['revisionDate'],
            riotAccountId = response['accountId'],
            riotId = response['id'],
            riotPuuid = response['puuid']
        )

        save_summoner(new_summoner)
        return new_summoner

def save_summoner(new_summoner):
    try:
        db.session.add(new_summoner)
        db.session.commit()
    except:
        return "There was an error adding summoner"

    return

def get_matches(summoner):

    # look up matches a summoner has played
    f = open("key.txt", "r")
    riot_key = f.read()
    watcher = LolWatcher(riot_key)
    region = 'na1'

    try:
        response = watcher.match.matchlist_by_account(region, summoner.riotAccountId)
        riot_match = response['matches'][0]['timestamp']

    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            return 'Summoner with that ridiculous name not found.'
        else:
            raise
        return err

    # Check if there are matches in DB
    if Match.query.filter_by(player=summoner).first() is not None:
        # Find most recent epoch timestamp if there are
        most_recent = (Match.query.filter_by(player=summoner).order_by(desc(Match.timestamp)).first()).timestamp
        split_matches = [ match for match in response['matches'] if match['timestamp'] > most_recent ]
        if len(split_matches) > 0:
            save_matches(split_matches, summoner)
        else:
            return Match.query.filter_by(player_id=summoner.id)

    else:
        save_matches(response['matches'], summoner)

def save_matches(match_list, summoner):

    for match in match_list:
        new_match = Match(
            player = summoner,
            gameId = match['gameId'],
            role = match['role'],
            season = match['season'],
            platformId = match['platformId'],
            champion = match['champion'],
            queue = match['queue'],
            lane = match['lane'],
            timestamp = match['timestamp']
        )

        try:
            db.session.add(new_match)
            db.session.commit()
        except:
            return "There was an error adding match"

    return

def get_best_champion(summoner):
    # Get all matches for summoner
    get_matches(summoner)
    
    pass

def get_champion(champion_id):
    # Looks up a champion based off of ID
    pass