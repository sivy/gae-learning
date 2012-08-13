from google.appengine.api import users
from google.appengine.ext import ndb
import datetime
import time

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)
DATE_FMT = "%Y-%m-%d %H:%M:%S"

class DictableModel(ndb.Model):
    def to_dict(self):
        output = {}

        for key, prop in self.properties().iteritems():
            value = getattr(self, key)

            if value is None or isinstance(value, SIMPLE_TYPES):
                output[key] = value
            elif isinstance(value, datetime.date):
                # Convert date/datetime to ms-since-epoch ("new Date()").
                # ms = time.mktime(value.utctimetuple())
                # ms += getattr(value, 'microseconds', 0) / 1000
                # output[key] = int(ms)
                output[key] = datetime.datetime.strftime(value, DATE_FMT)
            elif isinstance(value, ndb.GeoPt):
                output[key] = {'lat': value.lat, 'lon': value.lon}
            elif isinstance(value, ndb.Model):
                output[key] = to_dict(value)
            else:
                raise ValueError('cannot encode ' + repr(prop))

        return output


class Greeting(DictableModel):
    author = ndb.StringProperty()
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
    return ndb.Key('Guestbook', guestbook_name or 'test')