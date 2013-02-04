#!/usr/bin/env python

import threading
import urllib2
import nltk
from tfidf import TfIdf

from socket import *
from freesound.__init__ import *


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
    content.append(get_clean_text(url))

def print_keywords(document) :
    keywords = myTfIdf.get_doc_keywords(document)[0:5]
    print 'Top keywords: ',
    for (word, val) in keywords : print '%s' %(word),
    print

# SETTINGS
NUM_PAGES = 10000
corpus_filename = "corpus10k.txt"
stopwords_filename = "stopwords10k.txt"

myTfIdf = TfIdf(corpus_filename, stopwords_filename)

content = []
worker_threads = []

url = 'http://en.wikipedia.org/wiki/Special:Random'

for i in range(NUM_PAGES) :
    t = threading.Thread(target=clean_html_thread, args=(url, content,))
    t.start()
    worker_threads.append(t)

for t in worker_threads :
    t.join()

for t in worker_threads:
    if not t.isAlive():
        # get results from thtead
        t.handled = True
worker_threads = [t for t in worker_threads if not t.handled]

for document in content :
    myTfIdf.add_input_document(document)
    print_keywords(document)

myTfIdf.save_corpus_to_file(corpus_filename, stopwords_filename)


