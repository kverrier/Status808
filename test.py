import unittest
from myfreesound import MyFreeSound

class ServerTest(unittest.TestCase):

    def test_simple(self):
        url = 'http://localhost:8080/test.html'
        freesound_searcher = MyFreeSound()

        sound_urls = freesound_searcher.get_sounds_from_url(url)

        self.assertEqual(
            sound_urls, ['http://www.freesound.org/data/previews/14/14358_5190-lq.mp3',
                         'http://www.freesound.org/data/previews/111/111072_752810-lq.mp3',
                         'http://www.freesound.org/data/previews/170/170382_2368865-lq.mp3',
                         'http://www.freesound.org/data/previews/167/167165_1037961-lq.mp3',
                         'http://www.freesound.org/data/previews/169/169213_1956076-lq.mp3',
                         'http://www.freesound.org/data/previews/169/169212_1956076-lq.mp3',
                         'http://www.freesound.org/data/previews/169/169193_1956076-lq.mp3',
                         'http://www.freesound.org/data/previews/165/165913_1956076-lq.mp3'])


if __name__ == '__main__':

    unittest.main()
