import os
from django.utils import simplejson as json

from webtest import TestApp
from nose.tools import eq_, ok_

from google.appengine.ext import testbed

from main import app
from models import guestbook_key, Greeting

from fixture import FixtureLoader


class TestbedTest(object):
    def setUp(self):
        self.testapp = TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()


class TestIndex(TestbedTest):

    def test_index(self):
        response = self.testapp.get('/stremor')
        assert 'Guestbook' in str(response)

    def test_loggedin_index(self):
        os.environ['USER_EMAIL'] = 'testuser@example.com'
        os.environ['USER_ID'] = '123'
        os.environ['AUTH_DOMAIN'] = 'testbed'

        response = self.testapp.get('/stremor')

        ok_('Logout' in str(response))
        ok_('testuser' in str(response))

    def tearDown(self):
        self.testbed.deactivate()


class TestGreetings(TestbedTest):

    def test_post_greeting(self):
        response = self.testapp.post('/sign', {'guestbook_name': 'test', 'content': 'hi'})
        eq_(response.status, '302 Moved Temporarily')

        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                  guestbook_key('test'))

        ok_(greetings.count() == 1, 'There should be 1 Greeting object')

    def test_loggedin_post_greeting(self):
        os.environ['USER_EMAIL'] = 'testuser@example.com'
        os.environ['USER_ID'] = '123'
        os.environ['AUTH_DOMAIN'] = 'testbed'

        self.testapp.post('/sign', {'guestbook_name': 'test', 'content': 'hi'})

        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                 "ORDER BY date DESC LIMIT 10",
                                  guestbook_key('test'))
        greeting = greetings.fetch(1)[0]  # latest

        eq_(greeting.content, 'hi',
            'greeting content should be \'hi\'')
        eq_(greeting.author, 'testuser@example.com',
            'author content should be \'testuser@example.com\'')

    def tearDown(self):
        self.testbed.deactivate()


class TestAPI(object):

    def setUp(self):
        self.testapp = TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.loader = FixtureLoader()
        self.loader.load_data()

    def test_get_greetings(self):
        response = self.testapp.get('/api/greetings.json?guestbook=test')

        eq_(response.status, '200 OK')
        eq_(response.headers.get('Content-Type'), 'application/json')

        response_data = json.loads(response.body)
        eq_(len(response_data), 2, 'Greeting API should return 2 objects')
