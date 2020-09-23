import cassiopeia as cass
from cassiopeia import Summoner
from googletrans import Translator

cass.apply_settings('scoutahead\cass_settings.json')

def get_summoner(username):
    summoner_obj = Summoner(name=username, region="NA")
    summoner_obj.load()

    return summoner_obj

def get_japanese(word):
    translator = Translator()
    
    return translator.translate(word, dest='ja')