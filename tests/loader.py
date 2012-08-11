import os
from django.utils import simplejson as json
from nose.tools import ok_, eq_
from datetime import datetime

from main import Greeting, guestbook_key

DATE_FMT = "%Y-%m-%d %H:%M:%S"


def _class_name(fixture_class):
    return fixture_class.title().replace('_', '')


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
            'model': 'greeting',
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

                    m = __import__('main')
                    klass = getattr(m, klass_name)
                    instance = klass(parent=guestbook_key('test'))

                    for attr in [attr for attr in d.keys() if attr != 'model']:
                        value = d[attr]

                        try:
                            value = datetime.strptime(value, DATE_FMT)
                        except:
                            pass

                        instance.__setattr__(attr, value)

                    instance.put()


class TestLoader(object):
    def setUp(self):
        self.loader = FixtureLoader()
        self.loader.load_data()

    def test_loader(self):

        greeting_query = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                 guestbook_key('test'))
        greetings = greeting_query.fetch(10)

        ok_(greetings, 'Greetings should not be None')

        eq_(type(greetings), list)

        greeting1 = greetings[0]
        greeting2 = greetings[1]

        eq_(greeting1.author, 'testuser@example.com')
        eq_(greeting1.content, 'hi')
        eq_(greeting1.date, datetime.strptime('1971-06-29 04:13:01', DATE_FMT))

        eq_(greeting2.author, 'testuser@example.com')
        eq_(greeting2.content, 'bye')
        eq_(greeting2.date, datetime.strptime('1971-06-29 04:13:00', DATE_FMT))
