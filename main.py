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
# import cgi
import urllib
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname('__file__')
        + './templates'))

from google.appengine.api import users
from google.appengine.ext import db


class Greeting(db.Model):
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
    return db.Key.from_path('Guestbook', guestbook_name or 'stremor')


class MainPage(webapp2.RequestHandler):
    def get(self):

        guestbook_name = self.request.get('guestbook_name')  # or default_guestbook

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
        self.response.out.write(template.render(template_values))


class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        print "greeting: "
        if users.get_current_user():
            greeting.author = users.get_current_user().nickname()

        greeting.content = self.request.get('content')
        greeting.put()

        # redirect to home page
        self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/sign', Guestbook)],
                              debug=True)
