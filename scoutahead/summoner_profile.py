import cassiopeia as cass
from cassiopeia import Summoner
from googletrans import Translator
import random

cass.apply_settings('scoutahead\cass_settings.json')

def get_summoner(username):
    summoner_obj = Summoner(name=username, region="NA")
    summoner_obj.load()

    return summoner_obj

def get_translation(word, dest=None):

    if dest == None:
        languages = [
            'portuguese',
            'czech',
            'english',
            'greek',
            'hungarian',
            'polish',
            'romanian',
            'german',
            'spanish',
            'french',
            'italian',
            'russian',
            'turkish',
            'japanese',
            'korean'
        ]
    else:
        languages = [
            dest
        ]

    random.shuffle(languages)

    translator = Translator()
    
    translated = []

    translation = [ translated.append(translator.translate(word, dest=language)) for language in languages ]

    return translated