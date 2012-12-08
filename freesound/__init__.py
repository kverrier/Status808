# Largely based on canoris-python by Vincent Akkermans 

import httplib2, urllib2, urllib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import simplejson as json
from urllib2 import HTTPError
import re
from contextlib import contextmanager
import os

# Register the streaming http handlers with urllib2
register_openers()

BASE_URI                      = 'http://freesound.org/api'

_URI_SOUNDS                   = '/sounds'
_URI_SOUNDS_SEARCH            = '/sounds/search'
_URI_SOUNDS_CONTENT_SEARCH    = '/sounds/content_search'
_URI_SOUNDS_GEOTAG            = '/sounds/geotag'
_URI_SOUND                    = '/sounds/<sound_id>'
_URI_SOUND_ANALYSIS           = '/sounds/<sound_id>/analysis/<filter>'
_URI_SOUND_SIMILAR            = '/sounds/<sound_id>/similar'
_URI_USERS                    = '/people'
_URI_USER                     = '/people/<username>'
_URI_USER_SOUNDS              = '/people/<username>/sounds'
_URI_USER_PACKS               = '/people/<username>/packs'
_URI_USER_BOOKMARKS           = '/people/<username>/bookmark_categories'
_URI_BOOKMARK_CATEGORY_SOUNDS = '/people/<username>/bookmark_categories/<category_id>/sounds'
_URI_PACKS                    = '/packs'
_URI_PACK                     = '/packs/<pack_id>'
_URI_PACK_SOUNDS              = '/packs/<pack_id>/sounds'


def _uri(uri, *args):
    for a in args:
        uri = re.sub('<[\w_]+>', urllib.quote(str(a)), uri, 1)
    return BASE_URI+uri


class Freesound():

    __api_key = False

    @classmethod
    def set_api_key(cls, key):
        cls.__api_key = key

    @classmethod
    def get_api_key(cls):
        if not cls.__api_key:
            raise Exception("Please set the API key! --> Freesound.set_api_key(<your_key>)")
        return cls.__api_key

class RequestWithMethod(urllib2.Request):
    '''
    Workaround for using DELETE with urllib2.

    N.B. Taken from http://www.abhinandh.com/posts/making-a-http-delete-request-with-urllib2/
    '''
    def __init__(self, url, method, data=None, headers={},origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers,origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class FreesoundObject(object):

    def __init__(self, attrs):
        # If we only set the ref field we will set _loaded to false.
        # This way we can 'lazily' load the resource later on.
        self._loaded = False \
                       if len(attrs.keys())==1 and 'ref' in attrs \
                       else True
        self.attributes = attrs
    
    def __getitem__(self, name):
        # if the property isn't present, it might be because we haven't
        # loaded all the data yet.
        if not name in self.attributes:
            self.__load()
        # try to get the property
        return self.attributes[name]

    def __setitem__(self, name, val):
        raise NotImplementedError

    def __delitem__(self, name, val):
        raise NotImplementedError

    def keys(self):
        return self.attributes.keys()

    def __load(self):
        self.attributes = json.loads(_FSReq.simple_get(self['ref']))

    def get(self, name, default):
        return self.attributes.get(name, default)

    def update(self):
        self.__load()
        return self.attributes

class FreesoundException(Exception):
    def __init__(self, code, info):
        self.code = code
        self.explanation = info.get('explanation','')
        self.type = info.get('type','')
    def __str__(self):
        return '<FreesoundException: code=%s, type="%s", explanation="%s">' % \
                (self.code, self.type, self.explanation)


class _FSRetriever(urllib.FancyURLopener):
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        resp = fp.read()
        try:
            error = json.loads(resp)
        except:
            raise Exception(resp)
        raise FreesoundException(errcode,error)


class _FSReq(object):

    @classmethod
    def simple_get(cls, uri, params=False):
        return cls._simple_req(uri, 'GET', params)

    @classmethod
    def simple_del(cls, uri, params=False):
        return cls._simple_req(uri, 'DELETE', params)

    @classmethod
    def simple_post(cls, uri, params=False):
        return cls._simple_req(uri, 'POST', False, params)

    @classmethod
    def _simple_req(cls, uri, method, params, data=False):
        p = params if params else {}
        p['api_key'] = Freesound.get_api_key()
        u = '%s?%s' % (uri, urllib.urlencode(p))
        d = urllib.urlencode(data) if data else None
        req = RequestWithMethod(u, method, d)
        try:
            f = urllib2.urlopen(req)
        except HTTPError, e:
            resp = e.read()
            if e.code >= 200 and e.code < 300:
                return resp
            else:
                raise FreesoundException(e.code,json.loads(resp))
        resp = f.read()
        f.close()
        return resp

    @classmethod
    def retrieve(cls, url, path):
        return _FSRetriever().retrieve('%s?api_key=%s' % (url, Freesound.get_api_key()), path)

class PageException(Exception):
    pass

class Pager(FreesoundObject):

    @classmethod
    def _load_page(cls, uri, page, params={}):
        if page < 0:
            raise PageException('The page argument should be >= 0.')
	params['p']=page
        atts = json.loads(_FSReq.simple_get(uri, params))
        atts.update({'p_uri': uri,
		     'params':params})
        return Pager(atts)

    def next(self):
        if not 'next' in self.attributes:
            raise PageException('No more pages available.')
        self.__prev_next(1)

    def previous(self):
        if not 'previous' in self.attributes:
            raise PageException('You are already at page 1.')
        self.__prev_next(-1)

    def __prev_next(self, num):
        new_page = self.attributes['params']['p']+num
	self.attributes['params']['p'] = self.attributes['params']['p']+num
        new_attrs= json.loads(_FSReq.simple_get(self.attributes['p_uri'],
                                             self.attributes['params']))
        self.attributes.update(new_attrs)


class Sound(FreesoundObject):

    @staticmethod
    def get_sound(sound_id):
        return Sound.get_sound_from_ref(_uri(_URI_SOUND, sound_id))

    @staticmethod
    def get_sound_from_ref(ref):
        return Sound(json.loads(_FSReq.simple_get(ref)))

    @staticmethod
    def search(**params):#q query str, p page num, f filter, s sort
	p = 1
	if params.has_key('p'):
	    p = params['p']
	    del params['p']
	return Pager._load_page(_uri(_URI_SOUNDS_SEARCH),p,params)

    @staticmethod
    def content_based_search(**params):#t target features, f filter features, p page num, m max result
        p = 1
        if params.has_key('p'):
            p = params['p']
            del params['p']
	return Pager._load_page(_uri(_URI_SOUNDS_CONTENT_SEARCH),p,params)

    @staticmethod
    def geotag(**params):# latitude and longitude delimiters: min_lat, max_lat, min_lon, max_lon
        return json.loads(_FSReq.simple_get(_uri(_URI_SOUNDS_GEOTAG),params))

    def retrieve(self, directory, name=False):
        path = os.path.join(directory, name if name else self['original_filename'])
        return _FSReq.retrieve(self['serve'], path)
    
    def retrieve_preview(self, directory, name=False):
        path = os.path.join(directory, name if name else str(self['preview-hq-mp3'].split("/")[-1]))
        return _FSReq.retrieve(self['preview-hq-mp3'], path)

    def get_analysis(self, *filter, **kwargs):
        '''Retrieve the File's analysis.

        Arguments:

        any argument
          retrieve a certain part of the analysis tree

        Keyword arguments:

        showall
          retrieve all available analysis data (default: False)

        Example:

        ::

          file1.get_analysis('lowlevel', 'spectral_centroid', 'mean')
          file2.get_analysis(showall=True)

        Returns:

        Depending on the filter returns a dictionary, list, number, or string.
        '''
        return json.loads(
                 _FSReq.simple_get(
                    _uri(_URI_SOUND_ANALYSIS, self['id'], '/'.join(filter)),
                    params={'all': '1' if kwargs.get('showall', False) else '0'}))


    def get_similar(self, preset="lowlevel", num_results=15):
        '''Search for sounds that are similar to this one

        Arguments:

        preset
        #return json.loads(_FSReq.simple_get(_uri(_URI_SOUNDS_SEARCH),params))
          the similarity search preset to use ('music' or 'lowlevel')
        #return json.loads(_FSReq.simple_get(_uri(_URI_SOUNDS_SEARCH),params))
        #return json.loads(_FSReq.simple_get(_uri(_URI_SOUNDS_SEARCH),params))

        Keyword arguments:

        num_results
          the number of results to return

        Returns:

        a dictionary with the search results and number of sounds returned
        '''
        uri  = _uri(_URI_SOUND_SIMILAR, self['id'])
        return json.loads(_FSReq.simple_get(uri,params={'preset':preset, 'num_results':num_results}))

    def __repr__(self):
        return '<Sound: id="%s", name="%s">' % \
                (self['id'], self.get('original_filename','n.a.'))


class User(FreesoundObject):

    @staticmethod
    def get_user(username):
        return User(json.loads(_FSReq.simple_get(_uri(_URI_USER,username))))

    def sounds(self,p=1):
        return Pager._load_page(self['sounds'],p)
    
    def packs(self):
        return json.loads(_FSReq.simple_get(self['packs']))

    def bookmark_categories(self):
        return json.loads(_FSReq.simple_get(self['bookmark_categories']))

    def bookmark_category_sounds(self, uri, p=1): # category id can be an id or 'uncategorized'
        return Pager._load_page(uri,p)

    def __repr__(self):
        return '<User: "%s">' % \
                ( self.get('username','n.a.'))

class Pack(FreesoundObject):

    @staticmethod
    def get_pack(pack_id):
        return Pack(json.loads(_FSReq.simple_get(_uri(_URI_PACK,pack_id))))

    def sounds(self,p=1):
        return Pager._load_page(self['sounds'],p)

    def __repr__(self):
        return '<Pack:  name="%s">' % \
                ( self.get('name','n.a.'))
