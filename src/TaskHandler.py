# -*- coding: utf-8 -*-
import Crawler
import EmailSender
import re


class Handler(object):

    LOW_PRICE_TASK = "LowPriceDetection"

    def __init__(self, jsonParams):
        self.tasks = jsonParams['tasks']
        self.emailSender = EmailSender.Sender(jsonParams['gmailInfo'])

    def Dispatch(self):
        for task in self.tasks:
            self.ProcessTask(task)

    def ProcessTask(self, task):
        crawlerParams = {
            'board': task['board'],
            'blFromJson': True,
            'start': -(task['searchPages']),
            'end': -1
        }

        crawler = Crawler.PttWebCrawler(crawlerParams)
        articles = crawler.parse_articles()

        if self.LOW_PRICE_TASK == task['type']:
            self.HandleLowPriceTask(articles, task)

    def HandleLowPriceTask(self, articles, taskInfo):
        # with open(taskInfo['board'] + '.cache')

        for article in articles:
            if not self._IsContainEssentialKeyword(article, taskInfo['filterRule']):
                continue

            for target in taskInfo['filterRule']["multiTarget"]:
                if self._IsContainKeyword(article['article_title'], target["title"]) and \
                   self._IsLowPrice(article['content'], target['value'], target['keywordBeforeValue']):
                    self.emailSender.notifyClient(article, self.LOW_PRICE_TASK)
                    print('Detect!')

    @staticmethod
    def _IsContainEssentialKeyword(article, filterRule):
        title = article['article_title']
        content = article['content']

        print('Processing ' + title + '...')

        if not Handler._IsContainAllKeywords(title, filterRule['essential']['title']) or \
           not Handler._IsContainAllKeywords(content, filterRule['essential']['content']):
            return False

        return True

    @staticmethod
    def _IsContainKeyword(inputString, keywords):
        for word in keywords:
            if word in inputString:
                return True

        return False

    @staticmethod
    def _IsContainAllKeywords(inputString, keywords):
        for word in keywords:
            if word not in inputString:
                return False

        return True

    @staticmethod
    def _IsLowPrice(content, value, keywordBeforeValue):
        nums = [int(s) for s in re.findall(r'\d+', content)]

        for num in nums:
            if num < value and num > 100:
                return True

        return False
