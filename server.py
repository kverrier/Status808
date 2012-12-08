from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
#import urlparse
from urlparse import urlparse
import urllib2
import nltk
from tfidf import TfIdf

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

        myTfIdf = TfIdf("corpus.txt", "stopwords.txt")
        # Get HTML from a url
        html = response.read()

        # Strip tags and tokenize from HTML content
        clean_text = nltk.clean_html(html)

        #print url

        #get_clean_text(url)

        keywords = []
        for pair in myTfIdf.get_doc_keywords(clean_text)[0:5] :
            keywords.append(pair[0])

        info_msg = 'Top keywords for %s are %s' % (url, str(keywords))

        print info_msg



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


serve_on_port(8082)








