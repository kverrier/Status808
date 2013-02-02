import threading
from operator import itemgetter
from warnings import warn

from freesound.__init__ import *
from keywordgetter import KeyWordGetter


class MyFreeSound:
    def __init__(self):
        self.keyword_getter = KeyWordGetter()

    def get_sounds_from_url(self, url, num=8):
        """
        Return set of sounds (mp3 file urls) based on the contents of a html
        page url. Finds keywords and then queries them to freesound.org.
        """
        keywords = self.keyword_getter.get_keywords_from_url(url)
        print 'Top keywords for %s are %s' % (url, str(keywords))
        results = self.search_words(keywords)[0:num]
        if len(results) < num:
            warn('Could only find %d results instead of %d' % (
                len(results), num))

        return results

    def search_words(self, word_weight_pair):
        """
        Returns collection of sounds (mp3 file urls) sorted by relavence to
        inputed keywords with initial weights.
        """
        word_weight_pairs = []
        worker_threads = []

        # Freesound API calls block so use concurrent threads to increase
        # performance
        for pair in word_weight_pair:
            t = threading.Thread(target=worker, args=(pair, word_weight_pairs))
            t.start()
            worker_threads.append(t)
        for t in worker_threads:
            t.join()
        for t in worker_threads:
            if not t.isAlive():
                # get results from thtead
                t.handled = True
        worker_threads = [t for t in worker_threads if not t.handled]

        # After collecting all sound results from freesound
        # Sort sounds by second element (determined weight)
        return [url for (url, weight) in sorted(word_weight_pairs, key=itemgetter(1), reverse=True)]


def worker((keyword, tfidf), all_sound_pairs):
    """thread worker function"""
    t = threading.currentThread()
    all_sound_pairs.extend(search(keyword, tfidf))


def search(query, weight):
    """
    Search query string to Freesound.org and recieve results as a list of
    (url, weight) where the weight is intial_weight*DECREASE_FACTOR^i where i
    is the distance from the first result (used for sorting purposes).
    """
    Freesound.set_api_key('31ac7f49d68644c4bfafaf8213eddbc5')
    results = Sound.search(q=query, filter="duration:[1.0 TO 5.0]",
                           sort="rating_desc", max_results="3")
    DECREASE_FACTOR = .9  # decreate the weight farther away from top result

    sound_urls = []
    for sound in results['sounds']:
        sound_urls.append((sound['preview-lq-mp3'], weight))
        weight *= DECREASE_FACTOR

    return sound_urls
