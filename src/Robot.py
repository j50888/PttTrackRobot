# -*- coding: utf-8 -*-
import Crawler
import TaskHandler
import argparse
import Utils
import os

__version__ = '1.0'

def parseArgments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
        PTT tracker
    ''')
    parser.add_argument('-c', '--config', help='config path')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-t')

    args = parser.parse_args()

    params = {}

    if args.config:
        params['configPath']= args.config

    return params

if __name__ == '__main__':

    argParams = parseArgments()

    if 'configPath' in argParams:
        jsonParams = Utils.ParseJson(argParams['configPath'])
    else:
        jsonParams = Utils.ParseJson()

    handler = TaskHandler.Handler(jsonParams)
    handler.Dispatch()
