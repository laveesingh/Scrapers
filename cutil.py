from __future__ import print_function
import re
import os
import sys
import threading
import time
import requests
from bs4 import BeautifulSoup as Soup
from pprint import pprint
from pdfkit import from_url

FINISHED = 0
THREADS = 0
TOTAL = 0

def debug(msg, prog=False):
    global FINISHED, TOTAL, THREADS
    if TOTAL!= 0:
        hashes = int(FINISHED*25/TOTAL)
    else:
        hashes = 0
    progress = '[%s%s]' % ('#'*hashes, ' '*(25-hashes))
    if not prog: progress = ''
    print(' '*80, end='\r', file=sys.stderr)
    print(msg, progress, end='\r', file=sys.stderr)
    sys.stderr.flush()
    time.sleep(0.5)

def save_pdf(link, filename):
    try:
        from_url(link, filename, options={'quiet': ''})
    except:
        print("couldn't save for filename:%s"%filename)


def fetch_html(HTML_FILE, URL):
    # read html data of initial page
    if os.path.isfile(HTML_FILE):
        html = open(HTML_FILE, 'r').read()
        debug("local html found!")
    else:
        debug("fetching html from g4g...")
        response = requests.get(URL)
        if not response.ok:
            raise ConnectionError("Didn't get html data from g4g, bad connection")
        html = response.content
        with open(HTML_FILE, 'w') as f:
            f.write(html)
    return html

def fetch_topics(soup):
    ordered_lists = soup.findAll('ol')
    store = dict()
    debug("found %d ol tags!!!"%len(ordered_lists))
    debug("iterating ol tags")
    for ol in ordered_lists:
        title = ol.findPrevious('strong').text.strip().strip(':')
        title = re.sub(r'[ \/\-\[\]]', '_', title)
        store[title] = []
        for li in ol.findAll('li'):
            link = li.find('a').get('href')
            name = li.find('a').string
            store[title].append((name, link))
    return store
    
def store_to_articles(store):
    articles = []
    for title in store:
        debug('fetching archive for %s' % title )
        try:
            os.mkdir(title)
        except:
            None
        for article, link in store[title]:
            if not article:
                article = link.strip('/').split('/')[-1]
            article = re.sub(r'[ \/\-\[\]]', '_', article)
            filename = title + '/' + article + '.pdf'
            if not os.path.isfile(filename):
                articles.append((link, filename))
    return articles

def main(DIRNAME, URL, HTML_FILE):
    global THREADS, FINISHED, TOTAL
    html = fetch_html(HTML_FILE, URL)
    debug("creating soup...")
    soup = Soup(html, 'html.parser')
    store = fetch_topics(soup)
    debug('creating archive dir...')
    try:
        os.mkdir(DIRNAME)
        debug("created directory %s" % DIRNAME)
    except:
        debug("found directory %s" % DIRNAME)
    os.chdir(DIRNAME)
    articles = store_to_articles(store)
    debug("Found %d articles" % len(articles))
    TOTAL = len(articles)
    for link, filename in articles:
        debug("active threads: %d" % threading.active_count(), prog=True)
        while threading.active_count() > 10:
            time.sleep(3)
        threading.Thread(target=save_pdf, args=(link, filename)).start()
        THREADS += 1
        FINISHED = THREADS - threading.active_count()

    print('', file=sys.stderr)
