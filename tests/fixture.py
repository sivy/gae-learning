import os
from django.utils import simplejson as json
import datetime

from google.appengine.ext import db

DATE_FMT = "%Y-%m-%d %H:%M:%S"


def _class_name(fixture_class):
    return fixture_class.split('::')[1].title().replace('_', '')


# this is a stopgap until I get a better idea :-(
def _parent_key(fixture_class):
    parent, klass = fixture_class.split('::')
    bits = parent.split(':')
    return db.Key.from_path(bits[0], bits[1])


def _get_fixtures_dir(file):
    return os.path.realpath(os.path.dirname(file)) + "/fixtures"


class FixtureLoader(object):
    """ FixtureLoader

        - Look for json files in <project>/fixtures/*.json
        - Fixture is a json array, same as django fixtures
        - start by handling instanting
            - text properties
            - integer properties

        class Greeting(db.Model):
           author = db.StringProperty()
           content = db.StringProperty(multiline=True)
           date = db.DateTimeProperty(auto_now_add=True)

        {
            'model': 'ParentName:parent_value::model_name',
            'content': 'hi',
            'author': 'nickname',
            'date': '2010-15-04 12:12:12'
        }

    """
    def __init__(self):
        self.fixtures_dir = _get_fixtures_dir(__file__)

    def load_data(self):
        for root, dirs, files in os.walk(self.fixtures_dir):
            for f in files:
                fullpath = os.path.join(root, f)

                data_str = open(fullpath).read()
                print data_str
                data = []
                try:
                    data = json.loads(data_str)
                except Exception, e:
                    print e

                # where do we load classes from?

                for d in data:
                    klass_name = _class_name(d['model'])
                    parent_key = _parent_key(d['model'])

                    m = __import__('models')
                    klass = getattr(m, klass_name)

                    instance = klass(parent=parent_key)

                    for attr in [attr for attr in d.keys() if attr != 'model']:
                        value = d[attr]

                        try:
                            value = datetime.datetime.strptime(value, DATE_FMT)
                        except:
                            pass

                        instance.__setattr__(attr, value)

                    instance.put()
