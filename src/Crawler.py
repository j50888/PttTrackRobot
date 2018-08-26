# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import re
import sys
import json
import requests
import argparse
import time
import codecs
from bs4 import BeautifulSoup
from six import u

DEBUG = True

__version__ = '1.0'

# if python 2, disable verify flag in requests.get()
VERIFY = True
if sys.version_info[0] < 3:
    VERIFY = False
    requests.packages.urllib3.disable_warnings()


class PttWebCrawler(object):

    PTT_URL = 'https://www.ptt.cc'
    TIME_OUT = 5

    """docstring for PttWebCrawler"""
    def __init__(self, params, as_lib=False):
        self.board = params['board']

        if 'start' in params:
            if params['start'] < 0:
                self.start = self.getLastPage(self.board, params['start'])
            else:
                self.start = params['start']
            if params['end'] < 0:
                self.end = self.getLastPage(self.board, params['end'])
            else:
                self.end = params['end']

        if 'article_id' in params:
            self.article_id = params['article_id']

    def parse_articles(self, path='.', timeout=TIME_OUT):
        articles = []
        for i in range(self.end-self.start+1):
            index = self.start + i
            print('Processing index:', str(index))

            reqParams = {
                'url': self.PTT_URL + '/bbs/' + self.board + '/index' + str(index) + '.html',
                'cookies': {'over18': '1'},
                'verify': VERIFY,
                'timeout': timeout
            }

            resp = self.requestsWrapper(reqParams)
            if -1 == resp:
                continue

            if resp.status_code != 200:
                print('invalid url:', resp.url)
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            divs = soup.find_all("div", "r-ent")
            for div in divs:
                try:
                    # ex. link would be <a href="/bbs/PublicServan/M.1127742013.A.240.html">Re: [問題] 職等</a>
                    href = div.find('a')['href']
                    link = self.PTT_URL + href
                    article_id = re.sub('\.html', '', href.split('/')[-1])
                    parseResult = self.parse(link, article_id)

                    if -1 != parseResult:
                        articles.append(parseResult)
                except:
                    pass
            time.sleep(0.1)

        return articles

    def parse_article(self, path='.'):
        link = self.PTT_URL + '/bbs/' + self.board + '/' + self.article_id + '.html'
        filename = self.board + '-' + self.article_id + '.json'
        filename = os.path.join(path, filename)
        self.store(filename, self.parse(link, self.article_id, self.board), 'w')
        return filename

    @staticmethod
    def requestsWrapper(params):
        try:
            resp = requests.get(**params)
            return resp
        except (socket.timeout, requests.exceptions.ReadTimeout):
            print('Timeout! Skip this index.')
        except requests.exceptions.RequestException as e:
            print(e)
        except:
            print('Unkwon Error.')

        return -1

    @staticmethod
    def parse(link, article_id, timeout=TIME_OUT):
        print('Processing article:', article_id)


        reqParams = {
            'url': link,
            'cookies': {'over18': '1'},
            'verify': VERIFY,
            'timeout': timeout
        }

        resp = PttWebCrawler.requestsWrapper(reqParams)
        if -1 == resp:
            return -1

        if resp.status_code != 200:
            print('invalid url:', resp.url)
            return -1

        soup = BeautifulSoup(resp.text, 'html.parser')
        main_content = soup.find(id="main-content")
        metas = main_content.select('div.article-metaline')
        author = ''
        title = ''
        date = ''
        if metas:
            author = metas[0].select('span.article-meta-value')[0].string if metas[0].select('span.article-meta-value')[0] else author
            title = metas[1].select('span.article-meta-value')[0].string if metas[1].select('span.article-meta-value')[0] else title
            date = metas[2].select('span.article-meta-value')[0].string if metas[2].select('span.article-meta-value')[0] else date

            # remove meta nodes
            for meta in metas:
                meta.extract()
            for meta in main_content.select('div.article-metaline-right'):
                meta.extract()

        # remove and keep push nodes
        pushes = main_content.find_all('div', class_='push')
        for push in pushes:
            push.extract()

        try:
            ip = main_content.find(text=re.compile(u'※ 發信站:'))
            ip = re.search('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ip).group()
        except:
            ip = "None"

        # 移除 '※ 發信站:' (starts with u'\u203b'), '◆ From:' (starts with u'\u25c6'), 空行及多餘空白
        # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
        filtered = [ v for v in main_content.stripped_strings if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--'] ]
        expr = re.compile(u(r'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/-_.?~%()]'))
        for i in range(len(filtered)):
            filtered[i] = re.sub(expr, '', filtered[i])

        filtered = [_f for _f in filtered if _f]  # remove empty strings
        filtered = [x for x in filtered if article_id not in x]  # remove last line containing the url of the article
        content = ' '.join(filtered)
        content = re.sub(r'(\s)+', ' ', content)
        # print 'content', content

        # push messages
        p, b, n = 0, 0, 0
        messages = []
        for push in pushes:
            if not push.find('span', 'push-tag'):
                continue
            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
            # if find is None: find().strings -> list -> ' '.join; else the current way
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[1:].strip(' \t\n\r')  # remove ':'
            push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')
            messages.append( {'push_tag': push_tag, 'push_userid': push_userid, 'push_content': push_content, 'push_ipdatetime': push_ipdatetime} )
            if push_tag == u'推':
                p += 1
            elif push_tag == u'噓':
                b += 1
            else:
                n += 1

        # count: 推噓文相抵後的數量; all: 推文總數
        message_count = {'all': p+b+n, 'count': p-b, 'push': p, 'boo': b, "neutral": n}

        # print 'msgs', messages
        # print 'mscounts', message_count

        # json data
        data = {
            'url': link,
            'article_id': article_id,
            'article_title': title,
            'author': author,
            'date': date,
            'content': content,
            'ip': ip,
            'message_count': message_count,
            'messages': messages
        }
        # print 'original:', d

        return data

    @staticmethod
    def getLastPage(board, idx, timeout=TIME_OUT):
        content = requests.get(
            url= 'https://www.ptt.cc/bbs/' + board + '/index.html',
            cookies={'over18': '1'}, timeout=timeout
        ).content.decode('utf-8')
        first_page = re.search(r'href="/bbs/' + board + '/index(\d+).html">&lsaquo;', content)
        if first_page is None:
            print('first page is not found')
            return 1
        return int(first_page.group(1)) + 2 + idx

    @staticmethod
    def store(filename, data, mode):
        with codecs.open(filename, mode, encoding='utf-8') as f:
            f.write(data)

    @staticmethod
    def get(filename, mode='r'):
        with codecs.open(filename, mode, encoding='utf-8') as f:
            return json.load(f)

if __name__ == '__main__':
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


    crawler = PttWebCrawler(params)
    crawler.parse_articles()
