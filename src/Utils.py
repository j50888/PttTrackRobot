# -*- coding: utf-8 -*-
import json
import os
from pprint import pprint

DEBUG = False


def TrackGame(articles):
    for obj in articles:
        title = obj['article_title']
        print('Processing ' + title + '...')
        if 'NS' in title and '奧德賽' in title:
            print(obj['content'])


def ParseJson(filePath=os.path.join(os.path.dirname(__file__), '../config.json')):
    print('Parsing config.json...')

    with open(filePath, encoding='utf8') as file:
        data = json.load(file)

    if DEBUG:
        pprint(data)

    return data
