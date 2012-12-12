#!/usr/bin/env python

import logging

import threading
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from urlparse import urlparse
import urllib2
import nltk
from tfidf import TfIdf

from socket import *
from freesound.__init__ import *

from operator import itemgetter

#logging.basicConfig(level=logging.DEBUG,
                    #format='(%(threadName)-10s) %(message)s',
                    #)


def get_clean_text(URL) :
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(URL)

    # Get HTML from a url
    html = response.read()

    # Strip tags and tokenize from HTML content
    clean_text = nltk.clean_html(html)
    return clean_text



def clean_html_thread(url, content) :
    """thread worker function"""
    t = threading.currentThread()
    content.append(get_clean_text(url))
    logging.debug('ending')

def print_keywords(document) :
    keywords = myTfIdf.get_doc_keywords(document)[0:5]
    print 'Top keywords: ',
    for (word, val) in keywords : print '%s' %(word),
    print

#myTfIdf = TfIdf("corpus.txt", "stopwords.txt")
#myTfIdf = TfIdf("corpus100.txt", "stopwords100.txt")
myTfIdf = TfIdf("corpus10k.txt", "stopwords10k.txt")
NUM_PAGES = 1

content = []
worker_threads = []


url = 'http://en.wikipedia.org/wiki/Special:Random'

for i in range(NUM_PAGES) :
    t = threading.Thread(target=clean_html_thread, args=(url, content,))
    t.start()
    worker_threads.append(t)

for t in worker_threads :
    logging.debug('joining %s', t.getName())
    t.join()

for t in worker_threads:
    if not t.isAlive():
        # get results from thtead
        t.handled = True
worker_threads = [t for t in worker_threads if not t.handled]

for document in content :
    #myTfIdf.add_input_document(document)
    print 'Enter'
    print_keywords(document)
    print 'Exit'

#myTfIdf.save_corpus_to_file('corpus500.txt', 'stopwords500.txt')


