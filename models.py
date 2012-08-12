from google.appengine.api import users
from google.appengine.ext import db

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)


class DictableModel(db.Model):
    def to_dict(self):
        output = {}

        for key, prop in self.properties().iteritems():
            value = getattr(self, key)

            if value is None or isinstance(value, SIMPLE_TYPES):
                output[key] = value
            elif isinstance(value, datetime.date):
                # Convert date/datetime to ms-since-epoch ("new Date()").
                ms = time.mktime(value.utctimetuple())
                ms += getattr(value, 'microseconds', 0) / 1000
                output[key] = int(ms)
            elif isinstance(value, db.GeoPt):
                output[key] = {'lat': value.lat, 'lon': value.lon}
            elif isinstance(value, db.Model):
                output[key] = to_dict(value)
            else:
                raise ValueError('cannot encode ' + repr(prop))

        return output


class Greeting(DictableModel):
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
    return db.Key.from_path('Guestbook', guestbook_name or 'stremor')