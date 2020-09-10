import cassiopeia as cass
from cassiopeia import Summoner, Season, Queue, Champion, Champions, Patch, Position
from collections import OrderedDict
from operator import getitem, itemgetter
import operator, csv, roleml
from scoutahead.db import *
import datetime
import bs4

region = "NA"

# Cassiopeia settings
cass.apply_settings('cass_settings.json')
cass.set_default_region(region)

def testing():
    champs = Champions()
    for champion in champs:
        print(champion.tags)

def get_comps(summoners):

    team = summoners.lower().split(',')
    if len(team) < 5:
        #    return None
        pass

    #save_champ_role()
    
    #bring back compositions
    team_comps = []

    for player in team:
        # Summoner specific data
        summoner = Summoner(name=player, region=region)
        name = summoner.name
        profile_icon = summoner.profile_icon.id
        matches = summoner.match_history(begin_time=Patch.from_str("10.1").start, end_time=Patch.from_str("10.18").end, queues={Queue.ranked_solo_fives})
        cms = cass.get_champion_masteries(summoner=summoner, region=region)

        champion_id_to_name_mapping = {champion.id: champion.name for champion in cass.get_champions(region=region)}
        champions_played = {}

        roles = {
            'top': 0,
            'jungle': 0,
            'mid': 0,
            'bot': 0,
            'supp': 0
        }

        for match in matches:
            # Append predicted role from roleML
            match.timeline.load()
            match_loaded = match.load()
            if match.duration > datetime.timedelta(minutes=15):
                roleml.add_cass_predicted_roles(match_loaded)
                role = match.participants[summoner].predicted_role


            champion_id = match.participants[summoner].champion.id
            champion = champion_id_to_name_mapping[champion_id]
            participant_id = match.participants[summoner].id
            won = match.participants[summoner].team.win
            champion_obj = Champion(name=champion, id=champion_id)
            mastery_champ = cms.filter(lambda cm: cm.champion == champion_obj)
            mastery_level = ([cm.level for cm in mastery_champ])[0]
            mastery_points = ([cm.points for cm in mastery_champ])[0]

            if won == True:
                won = 1
            else:
                won = 0

            if role:
                roles[role] += 1

            if champion not in champions_played.keys():
                champions_played[champion] = {
                    'played': 1,
                    'won': won,
                    'win_rate': 0,
                    'mastery_level': mastery_level,
                    'mastery_points': mastery_points
                }
            else:
                played = champions_played[champion]['played']
                already_won = champions_played[champion]['won']
                champions_played[champion]['played'] = played + 1
                champions_played[champion]['won'] = already_won + won

        for champion in champions_played:
            win_rate = (int(champions_played[champion]['won']) / int(champions_played[champion]['played'])) * 100
            champions_played[champion]['win_rate'] = int(win_rate)

        # Sort by played then win rate
        sorted_champions = sorted(champions_played.items(), key=lambda x: (x[1]['played'], x[1]['mastery_points'], x[1]['win_rate']), reverse=True)
        pro_champions = [champ for champ in sorted_champions if champ[1]['mastery_level'] > 5]

        main_role = (max(roles, key=roles.get))

        if main_role == 'top':
            main_role = 'TOP'
        elif main_role == 'jungle':
            main_role = 'JUNGLE'
        elif main_role == 'mid':
            main_role = 'MIDDLE'
        elif main_role == 'bot':
            main_role = 'BOTTOM'
        else:
            main_role = 'UTILITY'
        
        pro_champ_with_roles = []

        champions = Champions()

        # Retrieve mtg and team comp roles
        for champion in pro_champions:

            try:
                play_rate = str(list((Champion(name=champion[0],region=region).play_rates).keys())[0]).upper().split('.')
                play_rate = play_rate[1]
                if play_rate not in main_role:
                    continue
            except:
                print("============ fucked up", champ.name)
                pass

            cr = ChampionRole.query.filter_by(name=champion[0]).first()

            queries = {}

            # find similar champions based on strict similarity
            for column in cr.__table__.columns:
                v = str(getattr(cr, column.name))
                # Match roles, power spikes, damage type, mtg color
                if v == "TRUE" or v == 'PHYSICAL' or v == 'MAGICAL' or v == 'UTILITY' or v == 'O':        
                    queries[column.name] = str(getattr(cr, column.name))

            sim_champions = ChampionRole.query.filter_by(**queries).all()

            # widen our search for those who have < 2
            if len(sim_champions) < 3:
                queries.clear()

                for column in cr.__table__.columns:
                    v = str(getattr(cr, column.name))
                    # Match roles, damage type
                    if v == "TRUE" or v == 'PHYSICAL' or v == 'MAGICAL' or v == 'UTILITY':
                        queries[column.name] = str(getattr(cr, column.name))
                
                sim_champions = ChampionRole.query.filter_by(**queries).all()

            # Widen search even further
            if len(sim_champions) < 3:
                queries.clear()

                for column in cr.__table__.columns:
                    v = str(getattr(cr, column.name))
                    if v == 'TRUE' or v == 'PHYSICAL' or v == 'MAGICAL' or v == 'UTILITY':
                        # Ignore power spikes
                        if column.name != 'early_game' and column.name != 'mid_game' and column.name != 'late_game':
                            queries[column.name] = str(getattr(cr, column.name))

                sim_champions = ChampionRole.query.filter_by(**queries).all()

            true_sim_champions = []

            for champ in sim_champions:

                kill_me = False
                if champ.name == champion[0]:
                    kill_me = True
                elif champ.name not in cms:
                    kill_me = True
                    break

                champ_ob = Champion(name=champ.name,region=region)
                try:
                    play_rate = str(list((champ_ob.play_rates).keys())[0]).upper().split('.')
                    play_rate = play_rate[1]
                    same_role = False

                    if play_rate not in main_role:
                        kill_me = True
                except:
                    print("============ fucked up", champ.name)
                    pass
                
                if kill_me == False:
                    true_sim_champions.append(champ)
            
            pro_champ_with_roles.append({
                'name': champion[0],
                'similar': true_sim_champions,
                'roles': queries,
                'win_rate': champion[1]['win_rate'],
                'mastery_level': champion[1]['mastery_level'],
                'mastery_points': champion[1]['mastery_points']
            })

        team_comps.append(
            {
                'name': summoner.name,
                'profile_icon': summoner.profile_icon.id,
                'role': main_role,
                'champions': pro_champ_with_roles
            }
        )
    return team_comps

def save_champ_role():
    with open('docs/MTG_COLORS.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for champion in reader:
            
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
