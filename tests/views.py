from webtest import TestApp
from main import app, Greeting, guestbook_key
from nose.tools import eq_, ok_

# from google.appengine.ext import testbed


class TestIndex(object):

    def setUp(self):
        self.testapp = TestApp(app)

    def test_index(self):
        response = self.testapp.get('/')
        assert 'Guestbook' in str(response)


class TestGreetings(object):

    def setUp(self):
        self.testapp = TestApp(app)

    def test_post_greeting(self):
        response = self.testapp.post('/sign', {'guestbook_name': 'test', 'content': 'hi'})
        eq_(response.status, '302 Moved Temporarily')

        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                  guestbook_key('test'))

        ok_(greetings.count() == 1, 'There should be 1 Greeting object')
