import logging

import threading
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from Queue import Queue


from urlparse import urlparse
import urllib2
import nltk
from tfidf import TfIdf

from socket import *
from freesound.__init__ import *

from operator import itemgetter

import timeit

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello World!")

        # Get url from query
        url = urlparse(self.path).query

        keywords = KeyWordGetter(url).get_keywords()

        print 'Top keywords for %s are %s' % (url, str(keywords))


        sound_pairs = []

        # Sequential Version
        #for (keyword, tfidf) in keywords :
            #sound_pair.extend( fs.search(keyword, tfidf) )

        # Concurrent Version using worker threads


        worker_threads = []
        for i in range(5) :
            t = threading.Thread(target=worker, args=(keywords[i], sound_pairs))
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

        # Sort pairs
        sound_pairs = sorted(sound_pairs, key=itemgetter(1),reverse=True)

        # TODO In between 8 sounds
        #sender = MaxMessageSender()
        num_sounds = 8
        if len(sound_pairs) >= num_sounds :
            i = 1
            for (url, weight) in sound_pairs[0 : num_sounds] :
                # format message for MAX MSP OSC-Route
                msg = "/%d decodeNetworkFileToBuf %s buf%d"%(i, url, i)
                sender.send_message(msg)
                i += 1
        else :
            print 'WARNING: Less than 8 sounds returned from freesound.org'

        sender.send_message('/randomize bang')



def worker((keyword, tfidf), all_sound_pairs) :
    """thread worker function"""
    t = threading.currentThread()
    all_sound_pairs.extend(fs.search(keyword, tfidf))
    logging.debug('ending')


class FreesoundSearcher :
    def search(self,query,weight):
        Freesound.set_api_key('31ac7f49d68644c4bfafaf8213eddbc5')
        results = Sound.search(q=query,filter="duration:[1.0 TO 5.0]",sort="rating_desc", max_results="3")
        DECREASE_FACTOR = .9 # decreate the weight farther away from top result

        #links = [(sound['preview-lq-mp3'], weight) for sound in results['sounds'] for weight*DECREASE_FACTOR** in range(0, len(results[sounds]))
        links = []
        for sound in results['sounds'] :
            links.append((sound['preview-lq-mp3'], weight))
            weight *= DECREASE_FACTOR

        return links

class MaxMessageSender():
    def __init__(self) :
        host = "localhost"
        port = 8085
        buf = 1024
        self.addr = (host, port)

        self.UDPSock = socket(AF_INET,SOCK_DGRAM)

    def send_message(self, data):
        if(self.UDPSock.sendto(data,self.addr)):
            print "Sending message '",data,"'....."

        #self.UDPSock.close()

# Grabs first 5 keywords
class KeyWordGetter():
    def __init__(self, url) :
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(url)

        # Get HTML from a url
        html = response.read()

        # Strip tags and tokenize from HTML content
        clean_text = nltk.clean_html(html)

        keywords = []
        for pair in myTfIdf.get_doc_keywords(clean_text)[0:5] :
            keywords.append(pair)

        self.keywords = keywords

    def get_keywords(self) :
        return self.keywords

    def get_clean_text(self, URL) :
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(URL)

        # Get HTML from a url
        html = response.read()

        # Strip tags and tokenize from HTML content
        clean_text = nltk.clean_html(html)
        return clean_text


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def serve_on_port(port):
    server = ThreadingHTTPServer(("localhost",port), Handler)
    server.serve_forever()


fs = FreesoundSearcher()
myTfIdf = TfIdf("corpus.txt", "stopwords.txt")
sender = MaxMessageSender()
serve_on_port(8082)


