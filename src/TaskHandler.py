import Crawler

DEBUG = True

class Handler(object):

    LOW_PRICE_TASK = 1

    def __init__(self, jsonParams):
        self.tasks = jsonParams['Tasks']
        self.pollingFreq = jsonParams['PollingFreq']

    def Dispatch(self):
        for task in self.tasks:
            self.ProcessTask(task)

    # @staticmethod
    def ProcessTask(self, task):
        crawlerParams = {
            'board': task['board'],
            'blFromJson': True,
            'start': -(task['searchPages']),
            'end': -1
        }

        crawler = Crawler.PttWebCrawler(crawlerParams)
        articles = crawler.parse_articles()

        if self.LOW_PRICE_TASK == task['Type']:
            self.HandleLowPriceTask(articles, task['filterRule'])

    @staticmethod
    def HandleLowPriceTask(articles, filterRule):
        for article in articles:
            title = article['article_title']
            blSkip = False

            if DEBUG:
                print('Processing ' + title + '...')

            for name in filterRule['queryTitle']:
                if name not in title:
                    blSkip = True

            if blSkip:
                continue

            print('found!')
