import os

from webtest import TestApp
from main import app, Greeting, guestbook_key
from nose.tools import eq_, ok_

from google.appengine.ext import testbed


class TestIndex(object):

    def setUp(self):
        self.testapp = TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def test_index(self):
        response = self.testapp.get('/')
        assert 'Guestbook' in str(response)

    def test_loggedin_index(self):
        os.environ['USER_EMAIL'] = 'testuser@example.com'
        os.environ['USER_ID'] = '123'
        os.environ['AUTH_DOMAIN'] = 'testbed'

        response = self.testapp.get('/')

        ok_('Logout' in str(response))
        ok_('testuser' in str(response))

    def tearDown(self):
        self.testbed.deactivate()


class TestGreetings(object):

    def setUp(self):
        self.testapp = TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

    def test_post_greeting(self):
        response = self.testapp.post('/sign', {'guestbook_name': 'test', 'content': 'hi'})
        eq_(response.status, '302 Moved Temporarily')

        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                  guestbook_key('test'))

        ok_(greetings.count() == 1, 'There should be 1 Greeting object')

    def test_loggedin_post_greeting(self):
        self.testapp.post('/sign', {'guestbook_name': 'test', 'content': 'hi'})

        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                  guestbook_key('test'))
        greeting = greetings.fetch(1)[0]  # latest

        ok_(greeting.content == 'hi', 'greeting content should be \'hi\'')

    def tearDown(self):
        self.testbed.deactivate()
