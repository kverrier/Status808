import nltk
import urllib2
from tfidf import TfIdf


class KeyWordGetter():
    """
    Class to determine the significant unique keywords of a page.
    Uses TF-IDF algorithm (http://en.wikipedia.org/wiki/Tf%E2%80%93idf).
    """

    def __init__(self):
        self.myTfIdf = TfIdf("corpus10k.txt", "stopwords10k.txt")

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        self.opener = opener

    def get_keywords_from_url(self, url, num_words=5, MAX_STR_LEN=1000):
        """
        Returns a list of tuples containing unique keywords of a page given a url and their
        significance as number between (0,1) using TF-IDF algorithm as a tuple.
        """
        clean_text = self.get_clean_text(url)

        if len(clean_text) > MAX_STR_LEN:
            clean_text = clean_text[:MAX_STR_LEN]

        keywords = []
        for pair in self.myTfIdf.get_doc_keywords(clean_text)[0: num_words]:
            keywords.append(pair)

        return keywords

    def get_clean_text(self, URL):
        """
        Returns the contents of a url's html page with tags removed
        """
        response = self.opener.open(URL)

        html = response.read()

        return nltk.clean_html(html)
