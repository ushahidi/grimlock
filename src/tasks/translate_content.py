import requests
import json
import logging
from config import settings
from microsofttranslator import Translator
import goslate


def run(data):
    if 'language' in data and 'code' in data['language'] and data['language']['code'] == 'en':
        return data

    
    """
    translator = Translator(settings.BING_APP_ID, settings.BING_APP_SECRET)
    
    try:
        data['contentEnglish'] = translator.translate(data['content'], "en")
    except Exception, e:
        print e
        pass
    """

    try:
      gs = goslate.Goslate()
      data['contentEnglish'] = gs.translate(data['content'][:1000], 'en')
    except Exception, e:
      print e
      pass

    return data