from riotwatcher import LolWatcher, ApiError
from datetime import datetime
from scoutahead.db import *
from sqlalchemy import desc, asc
from collections import OrderedDict
from operator import getitem
import json
import csv
import time

def get_team(team):

    team = team.lower().split(',')
    if len(team) < 5:
        #    return None
        pass
    summoners = []

    #assign_roles()

    for player in team:
        summoner = get_summoner(player)

        matches = get_matches(summoner)

        main_role = get_summoner_position(summoner)

        champions = get_best_champions(summoner, main_role)

        player_data = {
            'summoner': summoner,
            'champions': champions,
            'main_role': main_role
        }

        summoners.append(player_data)

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
            print('Summoner with that ridiculous name not found.')
        else:
            raise

    # Check if someone with this puuid already exists locally.
    if Summoner.query.filter_by(riotPuuid=response['puuid']).first() is not None:
        return Summoner.query.filter_by(riotPuuid=response['puuid']).first()

    else:
        new_summoner = Summoner(
            name=response['name'],
            profileIconId=response['profileIconId'],
            revisionDate=response['revisionDate'],
            riotAccountId=response['accountId'],
            riotId=response['id'],
            riotPuuid=response['puuid']
        )

        save_summoner(new_summoner)
        return new_summoner


def save_summoner(new_summoner):
    try:
        db.session.add(new_summoner)
        db.session.commit()
    except:
        return "There was an error adding summoner"

    return "Successfully saved summoner"


def get_matches(summoner):

    # look up matches a summoner has played
    f = open("key.txt", "r")
    riot_key = f.read()
    watcher = LolWatcher(riot_key)
    region = 'na1'

    try:
        response = watcher.match.matchlist_by_account(
            region, summoner.riotAccountId, 420, None, None, 0)
        riot_match = response['matches'][0]['timestamp']
        total_games = response['totalGames']
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise

    # Check if there are matches in DB
    if Match.query.filter_by(player=summoner).first() is not None:

        # Find most recent epoch timestamp if there are
        most_recent = (Match.query.filter_by(player=summoner).order_by(
            desc(Match.timestamp)).first()).timestamp
        split_matches = [match for match in response['matches']
                         if match['timestamp'] > most_recent]
        if len(split_matches) > 0:
            for match in split_matches:
                new_match = Match(
                    player=summoner,
                    gameId=match['gameId'],
                    role=match['role'],
                    season=match['season'],
                    platformId=match['platformId'],
                    champion=match['champion'],
                    queue=match['queue'],
                    lane=match['lane'],
                    position=get_lane(match['role'], match['lane']),
                    timestamp=match['timestamp']
                )
                get_match_detail(match['gameId'])
                save_match(new_match, summoner)
        else:
            matches = Match.query.filter_by(player=summoner).all()
            return matches

    else:

        #while response['endIndex'] != total_games:
        for match in response['matches']:
            print(f"Building match {match['gameId']}")
            new_match = Match(
                player=summoner,
                gameId=match['gameId'],
                role=match['role'],
                season=match['season'],
                platformId=match['platformId'],
                champion=match['champion'],
                queue=match['queue'],
                lane=match['lane'],
                position=get_lane(match['role'], match['lane']),
                timestamp=match['timestamp']
            )
            get_match_detail(match['gameId'])
            save_match(new_match, summoner)
            # just get 100 for now, that's fine
            #try:
            #    response = watcher.match.matchlist_by_account(
            #        region, summoner.riotAccountId, 420, None, None, response['endIndex'])
            #except ApiError as err:
            #    if err.response.status_code == 429:
            #        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            #        print('this retry-after is handled by default by the RiotWatcher library')
            #        print('future requests wait until the retry-after time passes')
            #    elif err.response.status_code == 404:
            #        print('Summoner with that ridiculous name not found.')
            #    else:
            #        raise

        #for match in response['matches']:
#
        #    new_match = Match(
        #        player=summoner,
        #        gameId=match['gameId'],
        #        role=match['role'],
        #        season=match['season'],
        #        platformId=match['platformId'],
        #        champion=match['champion'],
        #        queue=match['queue'],
        #        lane=match['lane'],
        #        position=get_lane(match['role'], match['lane']),
        #        timestamp=match['timestamp']
        #    )
#
        #    save_match(new_match, summoner)

    matches = Match.query.filter_by(player=summoner).all()
    return matches


def save_match(new_match, summoner):

    try:
        db.session.add(new_match)
        db.session.commit()
    except:
        return "There was an error adding match"

    return print("Successfully saved match", new_match)


def get_match_detail(game_id):

    if MatchDetail.query.filter_by(gameId=game_id).first() is not None:
        return MatchDetail.query.filter_by(gameId=game_id).first()

    else:

        # look up matches a summoner has played
        f = open("key.txt", "r")
        riot_key = f.read()
        watcher = LolWatcher(riot_key)
        region = 'na1'

        try:
            response = watcher.match.by_id(region, game_id)
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
                print('this retry-after is handled by default by the RiotWatcher library')
                print('future requests wait until the retry-after time passes')
            elif err.response.status_code == 404:
                print('Summoner with that ridiculous name not found.')
            else:
                raise

        match_detail = MatchDetail(
            object_args=response,
            gameId=game_id
        )

        save_match_detail(match_detail)

    return MatchDetail.query.filter_by(gameId=game_id).first()


def save_match_detail(match_detail):

    try:
        db.session.add(match_detail)
        db.session.commit()
    except:
        return "There was an error adding match"

    return print("Successfully saved match detail.", match_detail)


def get_best_champions(summoner, position):

    f = open("key.txt", "r")
    riot_key = f.read()
    watcher = LolWatcher(riot_key)
    region = 'na1'

    try:
        response = watcher.champion_mastery.by_summoner(region, summoner.riotId)
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise

    top_champs = []

    for champ in response:
        role = get_champion_role(champ['championId'])

    sub_set = response[0:5]

    for champ in sub_set:
        champ_id = champ['championId']
        champion_name = get_champion(champ_id)
        top_champs.append(champion_name)

    return top_champs


def get_champion(champion_id):
    # Looks up a champion based off of ID
    with open('static/current/data/en_US/championFull.json', encoding="utf-8") as json_file:
        champion_data = json.load(json_file)

        champion = champion_data["keys"][str(champion_id)]

    return champion

def get_lane(role, lane):
    position = ''
    print("role: ", role)
    print("lane: ", lane)
    if role == 'SOLO':
        if 'TOP' in lane:
            position = 'TOP'
        elif 'MID' in lane:
            position = 'MID'
        elif 'BOTTOM' in lane:
            position = 'TOP'
    elif role == 'DUO_CARRY':
        position = 'BOTTOM'
    elif role == 'DUO':
        if 'TOP' in lane:
            position = 'TOP'
        elif 'MID' in lane:
            position = 'MID'
    elif role == 'DUO_SUPPORT':
        position = 'UTILITY'
    elif role == 'NONE':
        position = 'JUNGLE'
    return position

def get_summoner_position(summoner):

    roles = {
        'TOP': 0,
        'JUNGLE': 0,
        'MID': 0,
        'BOTTOM': 0,
        'UTILITY': 0
    }

    for role in roles:
        matches = Match.query.filter_by(player=summoner,position=role).all()
        roles[role.upper()] = len(matches)
    
    position = max(roles, key=roles.get)
    
    if position == 'UTILITY':
        position = 'SUPPORT'

    return position

def get_champion_role(champion_id):

    champion_name = get_champion(champion_id)


# I hate this and am gonna make a better way to achieve it down the
def assign_roles():

    with open('docs/MTG_COLORS.csv', newline='') as csvfile:
        champion_data = csv.DictReader(csvfile)

        for champion in champion_data:
            hard_cc = False
            hard_engage = False
            disengage = False
            poke = False
            waveclear = False
            tank = False
            early_game = False
            mid_game = False
            late_game = False
            if champion['hard_cc'] == 'TRUE':
                hard_cc = True
            if champion['hard_engage'] == 'TRUE':
                hard_engage = True
            if champion['disengage'] == 'TRUE':
                disengage = True
            if champion['poke'] == 'TRUE':
                poke = True
            if champion['waveclear'] == 'TRUE':
                waveclear = True
            if champion['tank'] == 'TRUE':
                tank = True
            if champion['early_game'] == 'TRUE':
                early_game = True
            if champion['mid_game'] == 'TRUE':
                mid_game = True
            if champion['late_game'] == 'TRUE':
                late_game = True

            new_champion = Champion(
                name = champion['name'],
                damage = champion['damage'],
                red = champion['red'],
                green = champion['green'],
                blue = champion['blue'],
                white = champion['white'],
                black = champion['black'],
                colorless = champion['colorless'],
                hard_cc = hard_cc,
                hard_engage = hard_engage,
                disengage = disengage,
                poke = poke,
                waveclear = waveclear,
                tank = tank,
                early_game = early_game,
                mid_game = mid_game,
                late_game = late_game
            )

            try:
                db.session.add(new_champion)
                db.session.commit()
            except:
                return "There was an error adding champion"