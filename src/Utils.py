def TrackGame(articles):
    for obj in articles:
        title = obj['article_title']
        print('Processing ' + title + '...')
        if 'NS' in title and '奧德賽' in title:
            print(obj['content'])
