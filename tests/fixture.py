import os
from django.utils import simplejson as json
import datetime

from google.appengine.ext import ndb
from google.appengine.ext import testbed


DATE_FMT = "%Y-%m-%d %H:%M:%S"

import logging
log = logging.getLogger(__name__)

def _class_name(data):
    return data['model'].title().replace('_', '')


# this is a stopgap until I get a better idea :-(
def _ancestor_key(data):
    if 'ancestors' in data:
        pairs = [(pair['model'], pair['key']) for pair in data['ancestors']]
        print pairs
        return ndb.Key(pairs=pairs)
    return None


def _get_fixtures_dir(file):
    return os.path.realpath(os.path.dirname(file)) + "/fixtures"


class FixtureLoader(object):
    """ FixtureLoader

        - Look for json files in <project>/fixtures/*.json
        - Fixture is a json array, same as django fixtures
        - start by handling instanting
            - text properties
            - integer properties

        class Greeting(ndb.Model):
           author = ndb.StringProperty()
           content = ndb.StringProperty()
           date = ndb.DateTimeProperty(auto_now_add=True)

        {
            'model': 'ParentName:parent_value::model_name',
            'content': 'hi',
            'author': 'nickname',
            'date': '2010-15-04 12:12:12'
        }

    """
    def __init__(self):
        self.fixtures_dir = _get_fixtures_dir(__file__)

    def file_list(self, files):
        if hasattr(self, 'fixtures'):
            file_list = [file for file in files if file in self.fixtures]
        else:
            file_list = files
        return file_list

    def load_data(self, fixtures=None):
        for root, dirs, files in os.walk(self.fixtures_dir):
            for f in self.file_list(files):
                fullpath = os.path.join(root, f)

                data_str = open(fullpath).read()
                print data_str
                data = []
                try:
                    data = json.loads(data_str)
                except Exception, e:
                    log.exception(e)

                # where do we load classes from?

                for d in data:
                    klass_name = _class_name(d)
                    ancestor_key = _ancestor_key(d)
                    log.info(ancestor_key)
                    m = __import__('models')
                    klass = getattr(m, klass_name)

                    log.info(klass)

                    # instance = klass(parent=ancestor_key)
                    instance = klass()

                    for attr in [attr for attr in d.keys() if attr != 'model']:
                        value = d[attr]

                        try:
                            value = datetime.datetime.strptime(value, DATE_FMT)
                        except:
                            pass

                        instance.__setattr__(attr, value)

                    instance.put()


class FixtureTestClass(object):
    def __init__(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        if type(self.fixtures) == list:
            self.loader = FixtureLoader()
            self.loader.load_data(fixtures=self.fixtures)
