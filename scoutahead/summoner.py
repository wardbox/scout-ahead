from riotwatcher import LolWatcher, ApiError

def get_team(team):
    
    team = team.split(',')
    if len(team) < 5:
        return None

    summoners = []

    for player in team:
        summoner = get_summoner(player)
        summoners.append(summoner)

    return summoners

def get_summoner(summoner):

    f = open("key.txt", "r")
    riot_key = f.read()
    watcher = LolWatcher(riot_key)
    region = 'na1'

    try:
        response = watcher.summoner.by_name(region, summoner)
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise
    
    return response