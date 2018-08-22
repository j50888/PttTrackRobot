import Crawler
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', metavar=('START_INDEX', 'END_INDEX'), type=int, nargs=2, help="Start and end index")
    group.add_argument('-a', metavar='ARTICLE_ID', help="Article ID")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-t')

    args = parser.parse_args()

    params = {
        'board': args.b
    }

    if args.i:
        params['start'] = args.i[0]
        params['end'] = args.i[1]

    if args.a:  # args.a
        params['article_id'] = args.a

    return params

if __name__ == '__main__':

    Params = parseArgments()

    crawler = Crawler.PttWebCrawler(Params)
    articles = crawler.parse_articles()

    Utils.TrackGame(articles)
