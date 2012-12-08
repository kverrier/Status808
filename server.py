from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
#import urlparse
from urlparse import urlparse
import urllib2
import nltk
from tfidf import TfIdf
from socket import *
from freesound.__init__ import *

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello World!")

        url = urlparse(self.path).query

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(url)

        # Get HTML from a url
        html = response.read()

        # Strip tags and tokenize from HTML content
        clean_text = nltk.clean_html(html)


        keywords = []
        for pair in myTfIdf.get_doc_keywords(clean_text)[0:5] :
            keywords.append(pair[0])

        info_msg = 'Top keywords for %s are %s' % (url, str(keywords))

        print info_msg

        fs = FreesoundSearcher()

        sound_urls = []

        for keyword in keywords :
            sound_urls.append(fs.search(keyword))

        i = 1
        for sound_url in sound_urls :
            sender = MaxMessageSender()
            # format message for MAX MSP OSC-Route
            msg = "/%d decodeNetworkFileToBuf %s buf%d"%(i, sound_url, i)
            sender.send_message(msg)
            i += 1


class FreesoundSearcher :
    def search(self,query):
        Freesound.set_api_key('31ac7f49d68644c4bfafaf8213eddbc5')
        results = Sound.search(q=query,filter="duration:[1.0 TO 15.0]",sort="rating_desc", max_results="3")
        if results['sounds'] and results['sounds'][0] :
            return results['sounds'][0]['preview-lq-mp3']
        #for sound in results['sounds']:
            #print "\t- " + sound['original_filename'] + " --> " + sound['preview-lq-mp3']
        #print "\n"



class MaxMessageSender():
    def send_message(self, data):
        host = "localhost"
        port = 8085
        buf = 1024
        addr = (host, port)

        UDPSock = socket(AF_INET,SOCK_DGRAM)
        if(UDPSock.sendto(data,addr)):
            print "Sending message '",data,"'....."

        UDPSock.close()

class TextParser():
    def get_clean_text(URL) :
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


myTfIdf = TfIdf("corpus.txt", "stopwords.txt")
serve_on_port(8082)










