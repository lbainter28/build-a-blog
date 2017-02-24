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
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class MainPage(BlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * from BlogPost ORDER BY created DESC LIMIT 5")
        self.render("front.html", posts=posts)

class NewPost(BlogHandler):
    def get(self):
        self.render("new-post.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        error = ""

        if subject and content:
            post = BlogPost(subject=subject, content=content)
            post.put()
            post_id = post.key().id()
            post_address = '/blog/%s' % post_id
            self.redirect(post_address)
        else:
            error = "Please enter both a subject line and some content!"
            self.render("new-post.html", subject=subject, content=content, error=error)

class ViewPost(BlogHandler):
    def get(self, id):
        blog_post = BlogPost.get_by_id(int(id))
        #next_post = 
        self.render("view-post.html", blog_post=blog_post)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route(r'/blog/<id:\d+>', ViewPost)
], debug=True)
