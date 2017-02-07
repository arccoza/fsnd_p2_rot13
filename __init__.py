# import argparse
import re
from flask import Flask, request, render_template, redirect, url_for, abort
from google.appengine.ext import ndb


# parser = argparse.ArgumentParser(description='Run a webapp.')
# parser.add_argument('--port', type=int, help='The tcp/ip port to use.')
# args = parser.parse_args()
# print(args.port)

app = Flask(__name__, template_folder="views")


def rot13(text):
    for n, c in ((ord(c), c) for c in text):
      if 65 <= n <= 90:
        n += 13
        yield chr(n) if n <= 90 else chr(n - 26)
      elif 97 <= n <= 122:
        n += 13
        yield chr(n) if n <= 122 else chr(n - 26)
      else:
        yield c


class ErrorModel(object):
  def __getattr__(self, key):
    if key == '_data':
      return self.__dict__[key]
    return self._data.get(key)

  def __setattr__(self, key, val):
    if key == '_data':
      self.__dict__[key] = val
    else:
      self._data[key] = val

  def __init__(self):
    self._data = {}


class Validator(object):
  _tests = {
    'username': re.compile('^[a-zA-Z0-9_-]{3,20}$'),
    'password': re.compile('^.{3,20}$'),
    'email': re.compile('^[\S]+@[\S]+.[\S]+$')
  }

  @property
  def valid(self):
    for k, v in self.error._data.iteritems():
      if v:
        return False
    return True

  def __init__(self, input=None):
    self.error = ErrorModel()

  def validate(self, val, kind, required=True):
    if kind == 'same':
      return val[0] == val[1]
    return True if val and self._tests[kind].match(val) else not required


class AuthModel(Validator):
  @property
  def username(self):
    return self._data.get('username', 'a')

  @property
  def password(self):
    return self._data.get('password', '')

  @property
  def email(self):
    return self._data.get('email', '')

  def __init__(self, input=None):
    super(AuthModel, self).__init__()
    self._data = input or {}
    self.error.username = not self.validate(input.get('username'), 'username')
    self.error.password = not self.validate(input.get('password'), 'password')
    self.error.password_verify = not self.validate((input.get('password'),
                                                    input.get('verify')), 'same')
    self.error.email = not self.validate(input.get('email'), 'email')


@app.route("/rot13", methods=['GET', 'POST'])
def rot13_crypt():
  text = request.form.get('text', '')
  # print(text)
  text = ''.join(rot13(text))
  return render_template('rot13.html', text=text)


@app.route("/auth", methods=['GET', 'POST'])
def auth():
  a = AuthModel(request.form)
  print(a.error._data)
  print('-username-', a.error.username)
  if request.method == 'POST':
    print('---', a.error._data)
    if not a.valid:
      return render_template('auth.html', auth=a)
    return redirect(url_for('welcome', u=a.username))
  return render_template('auth.html', auth={'error': None})


@app.route("/welcome", methods=['GET'])
def welcome():
  return render_template('welcome.html', username=request.args.get('u'))


def not_empty(s, v):
  if v:
    return v
  else:
    raise TypeError(s._name + ' cannot be empty.')


class BlogPost(ndb.Model):
  subject = ndb.StringProperty(required=True, validator=not_empty)
  content = ndb.TextProperty(required=True, validator=not_empty)
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)


@app.route("/blog/", methods=['GET'])
@app.route("/blog/<int:post_id>", methods=['GET'])
def blog(post_id=None):
  if post_id:
    # print(post_id)
    post = ndb.Key(BlogPost, post_id).get()
    if not post:
      abort(404)
    return render_template('blog.html', post=post)

  try:
    posts = BlogPost.gql('ORDER BY created DESC LIMIT 10')
    return render_template('blog.html', posts=posts)
  except Exception as ex:
    print(ex)
    abort(404)


@app.route("/blog/newpost", methods=['GET', 'POST'])
def blog_newpost():
  # print('newpost')
  if request.method == 'POST':
    try:
      post = BlogPost(**request.form.to_dict())
      post_key = post.put()
    except TypeError as ex:
      # print(ex)
      return render_template('blog-newpost.html',
                             error='Invalid post, try again.',
                             subject=request.form.get('subject'),
                             content=request.form.get('content'))
    return redirect(url_for('blog', post_id=post_key.id()))
  return render_template('blog-newpost.html')


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080)
