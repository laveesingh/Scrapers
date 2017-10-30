# -*- coding: utf8 -*-

from __future__ import print_function
import os
import time
import threading
import sys
from cutil import debug, save_pdf, fetch_html
from bs4 import BeautifulSoup as Soup

HTML_FILE = 'ds.html'
URL = 'http://www.geeksforgeeks.org/data-structures/'
DIRNAME = 'data structures'

THREADS, FINISHED, TOTAL = 0, 0, 0

def fetch_articles(soup):
    topics = []
    debug("%d ordered lists found" % len(soup.findAll('ol')))
    for ol in soup.findAll('ol'):
        title = ol.findPrevious('strong').text.strip().strip(':').replace(' ', '_')
        try:
            os.mkdir(title)
        except:
            pass
        for anchor in ol.findAll('a'):
            link = anchor.get('href')
            if not link:
                continue
            name = anchor.text.strip()
            name = name.replace(u'’', '').replace('/', '_').replace(' ', '_')
            name = name.replace('?', '').replace('(', '_').replace(')', '_')
            if len(name) < 10:
                name = link.strip('/').split('/')[-1]
            name = title + '/' + name + '.pdf'
            topics.append((link, name))
    return topics

def main(HTML_FILE, URL, DIRNAME):
    global THREADS, TOTAL, FINISHED
    html = fetch_html(HTML_FILE, URL)
    debug('creating soup...')
    soup = Soup(html, 'html.parser')
    try:
        os.mkdir(DIRNAME)
        debug('created directory %s' % DIRNAME)
    except:
        debug('found directory %s' % DIRNAME)
    os.chdir(DIRNAME)
    articles = fetch_articles(soup)
    debug("Found %d articles" % len(articles))
    TOTAL = len(articles)
    for link, filename in articles:
        debug("active threads: %d" % threading.active_count(), prog=True)
        while threading.active_count() > 10:
            time.sleep(3)
        if not os.path.isfile(filename):
            threading.Thread(target=save_pdf, args=(link, filename)).start()
            THREADS += 1
        else:
            debug('found filename:%s' % filename)
            TOTAL -= 1
        FINISHED = THREADS - threading.active_count()
    print('', file=sys.stderr)

if __name__ == '__main__':
    main(HTML_FILE, URL, DIRNAME)
