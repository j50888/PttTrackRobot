import Crawler
import TaskHandler
import argparse
import Utils

__version__ = '1.0'

def parseArgments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
        A crawler for the web version of PTT, the largest online community in Taiwan.
        Input: board name and page indices (or articla ID)
        Output: BOARD_NAME-START_INDEX-END_INDEX.json (or BOARD_NAME-ID.json)
    ''')
    parser.add_argument('-b', metavar='BOARD_NAME', help='Board name', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', metavar=('START_INDEX', 'END_INDEX'), type=int, nargs=2, help="Start and end index")
    group.add_argument('-a', metavar='ARTICLE_ID', help="Article ID")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-t')

    args = parser.parse_args()

    crawlerParams = {
        'board': args.b
    }

    if args.i:
        crawlerParams['start'] = args.i[0]
        crawlerParams['end'] = args.i[1]
        crawlerParams['blFromJson'] = False

    if args.a:  # args.a
        crawlerParams['article_id'] = args.a
        crawlerParams['blFromJson'] = False

    params = {
        'blFromJson': args.a or args.i,
        'crawlerParams': crawlerParams
    }

    return params

if __name__ == '__main__':

    argParams = parseArgments()

    if argParams['blFromJson']:
        crawler = Crawler.PttWebCrawler(argParams['crawlerParams'])
        articles = crawler.parse_articles()
        Utils.TrackGame(articles)
    else:
        jsonParams = Utils.ParseJson()
        handler = TaskHandler.Handler(jsonParams)
        handler.Dispatch()
