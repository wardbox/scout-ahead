import cassiopeia as cass
from cassiopeia import Summoner, Patch, Queue
from collections import OrderedDict
from operator import getitem, itemgetter
import operator

# Cassiopeia settings
cass.apply_settings('cass_settings.json')
cass.set_default_region("NA")

def get_comps(summoners):

    team = summoners.lower().split(',')
    if len(team) < 5:
        #    return None
        pass

    #bring back compositions
    summoners = []

    for player in team:
        summoner = Summoner(name=player)
        name = summoner.name
        profile_icon = summoner.profile_icon.id
        matches = summoner.match_history(begin_time=Patch.from_str("10.12", region="NA").start, queues={Queue.ranked_solo_fives})

        champions_played = {}

        for match in matches:
            champion = match.participants[summoner].champion.name
            won = match.participants[summoner].team.win

            if won == True:
                won = 1
            else:
                won = 0

            if champion not in champions_played.keys():
                champions_played[champion] = {
                    'played': 1,
                    'won': won,
                    'win_rate': 0
                }
            else:
                played = champions_played[champion]['played']
                already_won = champions_played[champion]['won']
                champions_played[champion]['played'] = played + 1
                champions_played[champion]['won'] = already_won + won

        for champion in champions_played:
            win_rate = (int(champions_played[champion]['won']) / int(champions_played[champion]['played'])) * 100
            champions_played[champion]['win_rate'] = win_rate

        #sorted_champions = sorted(champions_played, key= operator.itemgetter(1, 'win_rate'), reverse=True)
        sorted_champions = sorted(champions_played, key=lambda x: ('played','win_rate'), reverse=True)
        print(sorted_champions)

        summoners.append({
            'name': name,
            'profile_icon': profile_icon
        })

    return summoners