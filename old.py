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



vocabulary = []
docs = {} # URL texts
hist = {}
stopwords = nltk.corpus.stopwords.words('english')
tokenizer = RegexpTokenizer( '\w+|\$[\d\.]+|\S+')


def freq(word, tokens):
    return tokens.count(word)

def word_count(tokens):
    return len(tokens)

def tf(word, tokens):
    return (freq(word, tokens) / float(word_count(tokens)))

def num_docs_containing(word, list_of_docs):
    count = 0
    for document in list_of_docs:
        if freq(word, document) > 0:
            count += 1
    return 1 + count

def idf(word, list_of_docs):
    return math.log(len(list_of_docs) /
            float(num_docs_containing(word, list_of_docs)))

def tf_idf(word, doc, list_of_docs):
    return (tf(word, doc) * idf(word, list_of_docs))



def process_page(URL) :
    # Get HTML from a url
    response = urllib2.urlopen(URL)
    html = response.read()

    # Strip tags and tokenize from HTML content
    content = BeautifulSoup(html).get_text()
    tokens = tokenizer.tokenize(content)

    bi_tokens = bigrams(tokens)
    tri_tokens = trigrams(tokens)
    tokens = [token.lower() for token in tokens if len(token) > 2]
    tokens = [token for token in tokens if token not in stopwords]

    #bi_tokens = [' '.join(token).lower() for token in bi_tokens]
    #bi_tokens = [token for token in bi_tokens if token not in stopwords]

    #tri_tokens = [' '.join(token).lower() for token in tri_tokens]
    #tri_tokens = [token for token in tri_tokens if token not in stopwords]

    final_tokens = []
    final_tokens.extend(tokens)
    #final_tokens.extend(bi_tokens)
    #final_tokens.extend(tri_tokens)

    docs[URL] = {'freq': {}, 'tf': {}, 'idf': {},
                        'tf-idf': {}, 'tokens': []}

    for token in final_tokens:
        #The frequency computed for each tip
        docs[URL]['freq'][token] = freq(token, final_tokens)
        #The term-frequency (Normalized Frequency)
        docs[URL]['tf'][token] = tf(token, final_tokens)

        docs[URL]['tokens'] = final_tokens

        hist[token] = tf(token, final_tokens)


if __name__ == "__main__" :

    test_url = "http://localhost:8081/hybrid/index.html"

    myTfIdf = TfIdf()

    print myTfIdf.get_num_docs()

    # Get HTML from a url
    response = urllib2.urlopen(test_url)
    html = response.read()

    # Strip tags and tokenize from HTML content
    content = BeautifulSoup(html).get_text()

    myTfIdf.add_input_document(content)

    print myTfIdf.get_doc_keywords(content)[0:3]

    print '---'


    process_page(test_url)

    #for entry in hist: print '%-10s ==> %10f' % (entry, hist[entry])

    for url in docs:
        for word in docs[url]:
            print url,
            print docs[url]['freq']
            #print '%-10s ==> f: %10d, tf: %10f, idf: %10f '% (word,
                    #data['freq'][word], data['tf'][word], data['idf'][word])
            #print "---"

    #print collections.Counter(hist).most_common()#[:-3:-1]

    #for token in final_tokens:
        #histo[token : freq(token, final_tokens)]

    hist = shelve.open("history", writeback=True)
    hist.close()





