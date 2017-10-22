from __future__ import print_function
import os
import time
import sys
import threading
from pprint import pprint
from bs4 import BeautifulSoup as Soup
from cutil import ( debug, save_pdf, fetch_html )

HTML_FILE = 'python.html'
URL = 'http://www.cdn.geeksforgeeks.org/python/'
DIRNAME = 'python'

THREADS, FINISHED, TOTAL = 0, 0, 0

def fetch_articles(soup):
    topic_list = ['Basics', 'Variables', 'Operators', 'Control Flow', 'Functions', 'Modules in Python', 'Object Oriented Concepts', 'Exception Handling', 'Libraries', 'Machine Learning with Python', 'Data Types', 'Misc', 'Applications and Projects', 'Multiple Choice Questions']
    topics = []
    for div in soup.findAll('div'):
        title = div.get('class')
        if not title: continue
        title = ' '.join(title)
        if title in topic_list:
            topics.append(( title, div ))

    store = []
    for title, div in topics:
        try:
            os.mkdir(title)
        except:
            None
        for anchor in div.findAll('a'):
            link = anchor.get('href')
            if not link:
                link = anchor.get('hrtef')
            link = link.strip('/')
            name = title + '/' + link.split('/')[-1] + '.pdf'
            store.append((link, name))
    return store


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
