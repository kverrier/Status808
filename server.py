import logging

from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from urlparse import urlparse

from myfreesound import MyFreeSound
from maxmessenger import MaxMessageSender

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        # Get url from query
        url = urlparse(self.path).query

        sound_urls = freesound_searcher.get_sounds_from_url(url)

        # Send sound urls to MAX MSP 
        for (i, url) in enumerate(sound_urls) :
            # Special formated message for MAX MSP OSC-Route
            msg = "/%d decodeNetworkFileToBuf %s buf%d"%(i+1, url, i+1)
            sender.send_message(msg)

        sender.send_message('/randomize bang')

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        keywords = ['dog', 'lupis']
        self.wfile.write(keywords)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def serve_on_port(port):
    server = ThreadingHTTPServer(("localhost",port), Handler)
    server.serve_forever()

if __name__ == '__main__':
    freesound_searcher = MyFreeSound()
    sender = MaxMessageSender()
    serve_on_port(8082)


