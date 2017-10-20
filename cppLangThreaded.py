import re
import os
import sys
import threading
import time
import requests
from bs4 import BeautifulSoup as Soup
from pprint import pprint
from pdfkit import from_url

def debug(msg):
    sys.stderr.write(msg)
    sys.stderr.flush()

def save_pdf(link, filename):
    from_url(link, filename, options={'quiet': ''})

# read html data of initial page
if os.path.isfile('cppLang.html'):
    html = open('cppLang.html', 'r').read()
    debug("Found html file locally, fetching html data...\n")
else:
    debug("fetching html from g4g...\n")
    response = requests.get("http://www.geeksforgeeks.org/c-plus-plus/")
    if not response.ok:
        raise ConnectionError("Didn't get html data from g4g, bad connection")
    html = response.content
    with open('cppLang.html', 'w') as f:
        f.write(html)

# create a navigable tree-like object from raw html
debug("creating soup...\n")
soup = Soup(html, 'html.parser')


ordered_lists = soup.findAll('ol')
store = dict()
debug("Iterating over all ordered lists...\n")
for ol in ordered_lists:
    title = ol.findPrevious('strong').text.strip().strip(':')
    title = re.sub(r'[ \/\-\[\]]', '_', title)
    store[title] = []
    for li in ol.findAll('li'):
        link = li.find('a').get('href')
        name = li.find('a').string
        store[title].append((name, link))
debug("Found %d unordered lists!!!\n"%len(store))
debug('creating directory for archive\n')
try:
    os.mkdir('CPP Archive')
except:
    debug("Found directory CPP Archive\n")
os.chdir('CPP Archive')
for title in store:
    debug('storing archive for %s\n' % title )
    try:
        os.mkdir(title)
    except:
        None
    for article, link in store[title]:
        debug("active threads: %d\n" % threading.active_count())
        while threading.active_count() > 15:
            time.sleep(5)
        if not article:
            article = link.strip('/').split('/')[-1]
        article = re.sub(r'[ \/\-\[\]]', '_', article)
        filename = title + '/' + article + '.pdf'
        # debug("filename: %s\n" % filename)
        if not os.path.isfile(filename):
            time.sleep(.5)
            threading.Thread(target=save_pdf, args=(link, filename)).start()
            # debug('.')
        else:
            debug('-')
    debug('\n')
