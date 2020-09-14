import cassiopeia as cass
from cassiopeia import Summoner, Season, Queue, Champion, Champions, Patch, Position
from collections import OrderedDict
from operator import getitem, itemgetter
import operator, csv, roleml, datetime
from scoutahead.db import *
from datetime import timedelta
import random
from itertools import combinations

region = "NA"
start_patch = "10.1"
end_patch = "10.18"

# Cassiopeia settings
cass.apply_settings('cass_settings.json')
cass.set_default_region(region)

def get_comps(summoners):

    team = summoners.lower().split(',')
    if len(team) < 5:
        #    return None
        pass

    # Maps names to champions so we don't have to make individual calls to the API
    cid_to_name_mapping = {champion.id: champion.name for champion in cass.get_champions(region=region)}

    #bring back compositions
    team_comps = []

    players = []

    champion_pool = []

    for player in team:

        # Summoner specific data
        summoner = Summoner(name=player, region=region)

        name = player

        try:
            profile_icon = summoner.profile_icon.id
        except:
            return None

        matches = summoner.match_history(begin_time=Patch.from_str(start_patch).start, end_time=Patch.from_str(end_patch).end, queues={Queue.ranked_solo_fives})

        # TO DO
        cms = cass.get_champion_masteries(summoner=summoner, region=region)

        match_stats = get_match_stats(
            matches,
            cms,
            summoner,
            cid_to_name_mapping
        )
        
        champion_details = get_champion_details(
            match_stats
        )

        for champ in champion_details:
            champion_pool.append(champ)

        players.append({
            'summoner': summoner,
            'main_role': match_stats['main_role'],
            'champions': champion_details,
            'match_stats': match_stats
        })

    team_comps = generate_team_comps(champion_pool)

    viable_comps = []

    for comp in team_comps:
        full = []
        for champion in comp:
            full.append(champion['role'])
        
        if 'UTILITY' in full and 'BOTTOM' in full and 'MIDDLE' in full and 'JUNGLE' in full and 'TOP' in full:
            for champion in comp:
                if champion['role'] == 'TOP':
                    top = champion
                elif champion['role'] == 'JUNGLE':
                    jungle = champion
                elif champion['role'] == 'MIDDLE':
                    middle = champion
                elif champion['role'] == 'BOTTOM':
                    bottom = champion
                else:
                    support = champion

            viable_comp = TeamComposition(
                top=top,
                jungle=jungle,
                mid=middle,
                bot=bottom,
                support=support
            )

            rating = viable_comp.assess_comp()

            if rating > 95:
                viable_comps.append({
                    'champions': viable_comp,
                    'rating': rating
                })

    for comp in viable_comps:
        print(comp['champions'].top)
        print(comp['champions'].jungle)
        print(comp['champions'].mid)
        print(comp['champions'].bot)
        print(comp['champions'].support)
        print(comp['rating'])

    return players

def get_champion_details(match_stats):

    champion_details = []

    # Retrieve mtg and team comp roles
    for champion in match_stats['champions']:

        champion_obj = Champion(name=champion[0], region=region)

        champion_role = get_champion_role(champion_obj)

        if champion_role != match_stats['main_role']:
            continue

        similar_champions = get_similar_champions(champion_obj, match_stats['main_role'], strict=True)

        if len(similar_champions) < 2:
            similar_champions = get_similar_champions(champion_obj,  match_stats['main_role'], lenient=True)

        filtered_similar = []

        for champion in similar_champions:
            if champion.name != champion_obj.name:
                filtered_similar.append(champion)
        
        champion_details.append({
            'name': champion_obj.name,
            'similar': filtered_similar,
            'role': champion_role
        })

    return champion_details

def get_similar_champions(champion, main_role, strict=False, lenient=False):

    champion_detail = ChampionRole.query.filter_by(name=champion.name).first()

    query = {}

    if strict == True:
        # find similar champions based on strict similarity
        for column in champion_detail.__table__.columns:
            v = str(getattr(champion_detail, column.name))
            # Match roles, power spikes, damage type, mtg color
            if v == "1" or v == 'PHYSICAL' or v == 'MAGICAL' or v == 'UTILITY' or v == 'X':        
                query[column.name] = str(getattr(champion_detail, column.name))        

    elif lenient == True:
        for column in champion_detail.__table__.columns:
            v = str(getattr(champion_detail, column.name))
            if v == '1' or v == 'PHYSICAL' or v == 'MAGICAL' or v == 'UTILITY':
                # Ignore power spikes
                if column.name != 'early_game' and column.name != 'mid_game' and column.name != 'late_game':
                    query[column.name] = str(getattr(champion_detail, column.name))
    else:
        return print("You gotta identify what strength the search is using my dude.")

    similar_champions = ChampionRole.query.filter_by(**query).all()

    similar_and_same_role = []

    for champion in similar_champions:
        champion_role = get_champion_role(Champion(name=champion.name, region=region))
        if champion_role == main_role:
            similar_and_same_role.append(champion)

    return similar_and_same_role

def get_match_stats(matches, champion_masteries, summoner, name_mapping):

    champions_played = {}

    # TO DO - use counter object instead
    roles = {
        'top': 0,
        'jungle': 0,
        'mid': 0,
        'bot': 0,
        'supp': 0
    }

    for match in matches:

        # Append predicted role of champion
        match_loaded = match.load()
        match_loaded.timeline.load()

        if match.duration > timedelta(minutes=15):
            roleml.add_cass_predicted_roles(match_loaded)
            predicted_role = match.participants[summoner].predicted_role
        
        # This relates to the counter object TO DO, if this comment exists blame wardbox
        roles[predicted_role] += 1

        # Match specific info on the summoner
        participant_id = match.participants[summoner].id
        won = match.participants[summoner].team.win

        # Champion played that match
        champion_id = match.participants[summoner].champion.id
        champion_name = name_mapping[champion_id]
        champion_obj = Champion(name=champion_name, id=champion_id)

        # Mastery of the champion played that match - not making another call to API for mastery :)
        mastery_champ = champion_masteries.filter(lambda cm: cm.champion == champion_obj)
        mastery_level = ([cm.level for cm in mastery_champ])[0]
        mastery_points = ([cm.points for cm in mastery_champ])[0]

        if won == True:
            won = 1
        else:
            won = 0

        if champion_name not in champions_played.keys():
            champions_played[champion_name] = ChampionStat(
                won = won,
                mastery_level = mastery_level,
                mastery_points = mastery_points,
                win_rate = 0
            )
        else:
            champ = champions_played[champion_name]
            champ.played += 1
            champ.won += won
            champ.win_rate = int((champ.won / champ.played) * 100)

    # Sort by played then win rate
    sorted_champions = sorted(champions_played.items(), key=lambda x: (x[1].played, x[1].mastery_points, x[1].win_rate), reverse=True)
    pro_champions = [champ for champ in sorted_champions if champ[1].mastery_level > 4]

    main_role = (max(roles, key=roles.get))

    if main_role == 'top':
        main_role = 'TOP'
    elif main_role == 'jungle':
        main_role = 'JUNGLE'
    elif main_role == 'mid':
        main_role = 'MIDDLE'
    elif main_role == 'bot':
        main_role = 'BOTTOM'
    elif main_role == 'supp':
        main_role = 'UTILITY'
    else:
        main_role = 'UNDETERMINED'
        
    return {
        'champions': sorted_champions,
        'main_role': main_role
    }

def save_champ_detail():

    db.session.query(ChampionRole).delete()
    db.session.commit()

    with open('docs/MTG_COLORS.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for champion in reader:
            if ChampionRole.query.filter_by(name=champion['name']).first() is None:
                new_champion = ChampionRole(
                    name = champion['name'],
                    hard_cc = champion['hard_cc'],
                    hard_engage = champion['hard_engage'],
                    disengage = champion['disengage'],
                    poke = champion['poke'],
                    waveclear = champion['waveclear'],
                    tank = champion['tank'],
                    damage = champion['damage'],
                    early_game = champion['early_game'],
                    mid_game = champion['mid_game'],
                    late_game = champion['late_game'],
                    red = champion['red'],
                    green = champion['green'],
                    blue = champion['blue'],
                    white = champion['white'],
                    black = champion['black'],
                    colorless = champion['colorless']
                )

                try:
                    db.session.add(new_champion)
                    db.session.commit()
                except:
                    print("Error saving to DB.")

def get_champion_role(champion):

    play_rate = str(list((champion.play_rates).keys())[0]).upper().split('.')
    return play_rate[1]

class ChampionStat(object):

    def __init__(self, won, mastery_level, mastery_points, played=1, win_rate=0):
        self.played = played
        self.won = won
        self.mastery_level = mastery_level
        self.mastery_points = mastery_points
        self.win_rate = win_rate

class TeamComposition():

    def __init__(self, top, jungle, mid, bot, support):
        self.top = top
        self.jungle = jungle
        self.mid = mid
        self.bot = bot
        self.support = support

    def assess_comp(self):

        scores = []

        good_comp = {
            'hard_cc': 3,
            'hard_engage': 2,
            'disengage': 1,
            'poke': 1,
            'waveclear': 1,
            'tank': 2,
            'PHYSICAL': 1,
            'MAGICAL': 1,
            'UTILITY': 1,
            'early_game': 1,
            'mid_game': 1,
            'late_game': 2
        }

        our_comp = {
            'hard_cc': 0,
            'hard_engage': 0,
            'disengage': 0,
            'poke': 0,
            'waveclear': 0,
            'tank': 0,
            'PHYSICAL': 0,
            'MAGICAL': 0,
            'UTILITY': 0,
            'early_game': 0,
            'mid_game': 0,
            'late_game': 0
        }

        for champion in vars(self).values():

            champion_detail = ChampionRole.query.filter_by(name=champion['name']).first()

            # find similar champions based on strict similarity
            for column in champion_detail.__table__.columns:
                v = str(getattr(champion_detail, column.name))
                # Match roles, power spikes, damage type, mtg color
                if v == "1":        
                    our_comp[column.name] += 1
                elif v == 'PHYSICAL' or v == 'MAGICAL' or v == 'UTILITY':
                    our_comp[v] += 1

        for role in our_comp:
            role_minimum = good_comp[role]

            if our_comp[role] < role_minimum:
                scores.append(our_comp[role] / role_minimum)
            else:
                scores.append(1)

        return int((sum(scores) / len(scores)) * 100)

def generate_team_comps(champions):

    combinations_list = list(combinations(champions, 5))
    return combinations_list