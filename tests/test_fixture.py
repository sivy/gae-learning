from nose.tools import ok_, eq_
from datetime import datetime

from models import Greeting, guestbook_key, DATE_FMT

from google.appengine.ext import testbed

from fixture import FixtureLoader


class TestFixtureLoader(object):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.loader = FixtureLoader()
        self.loader.load_data()

    def test_loader(self):

        greeting_query = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                 guestbook_key('test'))
        eq_(greeting_query.count(), 2, 'There should be 2 Greetings')

        greetings = greeting_query.fetch(10)
        ok_(greetings, 'Greetings should not be None')

        eq_(type(greetings), list, 'greetings should be a list')
        eq_(len(greetings), 2, '2 Greetings should be fetched')

        greeting1 = greetings[0]
        greeting2 = greetings[1]

        eq_(greeting1.author, 'testuser@example.com')
        eq_(greeting1.content, 'hi')
        eq_(greeting1.date, datetime.strptime('1971-06-29 04:13:01', DATE_FMT))

        eq_(greeting2.author, 'testuser@example.com')
        eq_(greeting2.content, 'bye')
        eq_(greeting2.date, datetime.strptime('1971-06-29 04:13:00', DATE_FMT))

        d = greeting1.to_dict()
        eq_(d['content'], greeting1.content)
        eq_(d['author'], greeting1.author)

    def tearDown(self):
        self.testbed.deactivate()
