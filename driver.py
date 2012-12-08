#!/usr/bin/env python

import math
import collections
import nltk
from nltk import RegexpTokenizer
from nltk import bigrams
from nltk import trigrams
from operator import itemgetter
from bs4 import BeautifulSoup
from pprint import pprint
import urllib2
import shelve
from tfidf import TfIdf
from time import clock

def get_clean_text(URL) :
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(URL)

    # Get HTML from a url
    #response = urllib2.urlopen(URL)
    html = response.read()

    # Strip tags and tokenize from HTML content
    clean_text = nltk.clean_html(html)
    return clean_text


if __name__ == "__main__" :

    start = clock()

    myTfIdf = TfIdf("corpus.txt", "stopwords.txt")

    test_urls = [
            #"http://localhost:8081/hybrid/index.html",
            ]

    for url in test_urls :
        clean_text = get_clean_text(url)
        myTfIdf.add_input_document(clean_text)


    # Grab some Wikipedia Data
    #for i in xrange(10):
        #for j in xrange(100):
            #clean_text = get_clean_text("http://en.wikipedia.org/wiki/Special:Random")
            #myTfIdf.add_input_document(clean_text)
        #print "Processed 100. Writing to disk..."
        #myTfIdf.save_corpus_to_file("corpus.txt", "stopwords.txt")

    # Grab some NY Times Data
    #for i in xrange(10):
        #clean_text = get_clean_text("http://nytimes-roulette.appspot.com/r")
        #myTfIdf.add_input_document(clean_text)


    sample_text = get_clean_text("

    count = 1
    print "TOP 5 Keywords"
    print "=============="
    for value in myTfIdf.get_doc_keywords(sample_text)[0:5] :
        print '%d) %s' % (count, value[0])
        count += 1

    myTfIdf.save_corpus_to_file("corpus.txt", "stopwords.txt")

    elapsed = (clock() - start)
    print "TIME ELAPSED: %f CPU seconds" % (elapsed)


