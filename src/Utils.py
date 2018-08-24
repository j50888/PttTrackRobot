# -*- coding: utf-8 -*-
import json
import os
from pprint import pprint

DEBUG = True

def TrackGame(articles):
    for obj in articles:
        title = obj['article_title']
        print('Processing ' + title + '...')
        if 'NS' in title and '奧德賽' in title:
            print(obj['content'])

def ParseJson():
    print('Parsing config.json...')

    curDir = os.path.dirname(__file__)
    configPath = os.path.join(curDir, '../config.json')

    with open(configPath, encoding = 'utf8') as file:
        data = json.load(file)

    if DEBUG:
        pprint(data)

    return data
