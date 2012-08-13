#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2
import os
from datetime import datetime

from django.utils import simplejson as json

DATE_FMT = "%Y-%m-%d %H:%M:%S"

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname('__file__')
        + './templates'))

from google.appengine.api import users
from google.appengine.ext import ndb

from models import Greeting, guestbook_key


class MainPage(webapp2.RequestHandler):
    def get(self, guestbook_name='stremor'):

        # SELECT * FROM is a given when used in Model context
        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                "ORDER BY date DESC LIMIT 10",
                                guestbook_key(guestbook_name))

        user = users.get_current_user()
        user_nick = ''
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            user_nick = user.nickname()
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'guestbook_name': guestbook_name,
            'greetings': greetings,
            'user_nick': user_nick,
            'url_linktext': url_linktext,
            'url': url
        }

        template = jinja_environment.get_template('index.html')

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(template.render(template_values))


class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user().nickname()

        greeting.content = self.request.get('content')
        greeting.put()

        # redirect to home page
        self.redirect('/%s' % guestbook_name)


class GuestbookAPI(webapp2.RequestHandler):
    def get(self):
        guestbook = self.request.get('guestbook')
        greetings = Greeting.gql("WHERE ANCESTOR IS :1 "
                                "ORDER BY date DESC LIMIT 10",
                                guestbook_key(guestbook))

        # this ought to be a lot smarter
        d = []
        for greeting in greetings.fetch(10):
            d.append({
                'content': greeting.content,
                'author': greeting.author,
                'datetime': datetime.strftime(greeting.date, DATE_FMT)
                })

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(d))


app = webapp2.WSGIApplication([
    (r'/sign', Guestbook),
    (r'/api/greetings.json', GuestbookAPI),
    (r'/([\w_]+)', MainPage)
], debug=True)
