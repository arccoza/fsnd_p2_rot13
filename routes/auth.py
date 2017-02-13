from flask import Blueprint, request, make_response, render_template, redirect, url_for, abort
from jinja2 import TemplateNotFound
from models.auth import User
from collections import namedtuple
from jose import jwt


auth_pages = Blueprint('auth', __name__, template_folder='views')
Conf = namedtuple('Conf', ['SESSION_SECRET'])
conf = Conf('sssshhhhhhhhhhhh!')


def set_session(user):
  token = jwt.encode({'username': user.username},
                     conf.SESSION_SECRET, algorithm='HS256')
  print(token)


def get_session(token):
  return jwt.decode(token, conf.SESSION_SECRET, algorithms=['HS256'])


class Token(dict):
  def __init__(self, *args, **kwargs):
    super(Token, self).__init__(*args, **kwargs)
    self.secret = None
    self.algorithm = 'HS256'
    self._value = None

  def __setitem__(self, k, v):
    super(Token, self).__setitem__(k, v)
    self._value = None

  def __delitem__(self, k):
    super(Token, self).__delitem__(k)
    self._value = None

  def update(self, it):
    super(Token, self).update(it)
    self._value = None

  # TODO: Make this safer.
  def reset(self, val):
    val.__iter__
    self.clear()
    self.update(val)
    # self._value = None

  def encode(self):
    if not self._value:
      print('----------------', self.secret)
      self._value = jwt.encode(self, self.secret, algorithm=self.algorithm)
    return self._value

  def _decode(self, token=None):
    return jwt.decode(token or self._value,
                      self.secret, algorithms=[self.algorithm])

  def decode(self, token):
    val = self._decode(token)
    self.reset(val)
    return self

  def __str__(self):
    return self.encode()


class Session(object):
  def __init__(self):
    self._token = Token()


class Security(object):
  def __init__(self):
    self._token = Token()

  @property
  def token(self):
    return self._token

  @token.setter
  def token(self, v):
    try:
      self._token.decode(v)
    except:
      self._token.reset(v)


# class Session(dict):
#   def __init__(self, *args, **kwargs):
#     super(Session, self).__init__(*args, **kwargs)
#     self.secret = None
#     self.algorithm = 'HS256'
#     self.session_name = 'session'

#   def to_token(self):
#     return jwt.encode(self,
#                      self.secret, algorithm=self.algorithm)
#   def _from_token(self, token):
#     return jwt.decode(token, self.secret, algorithms=[self.algorithm])

#   def from_token(self, token):
#     val = self._from_token(token)
#     self.clear()
#     self.update(val)
#     return self

#   def get_session(self, req):
#     tok = req.cookies.get(self.session_name)
#     self.from_token(tok)

#   def set_session(self, res):
#     res.set_cookie(self.session_name, value=self.to_token(), path='/')

#   def del_session(self, res):
#     res.set_cookie(self.session_name, value='', expires=0, path='/')


@auth_pages.route('/signup/', methods=['GET', 'POST'])
def signup():
  # u = User(username='test', password='1234', email='test@mail.com')
  # u.put()
  # print(u._values)
  # user_exists = User.query(User._properties['username'] == 'bobby').get()
  # print(user_exists)
  user = None
  pass_verified = None
  if request.method == 'POST':
    try:
      user = User()
      user.fill(**request.form.to_dict())
      pass_verified = request.form.get('verify') == request.form.get('password')
      if user.valid() and user.unique and pass_verified:
        user.put()
        return redirect('/')
    except Exception as ex:
      print('bad user')
  try:
    return render_template('signup.html', auth=user, pass_verified=pass_verified)
  except TemplateNotFound:
    abort(404)


@auth_pages.route('/login/', methods=['GET', 'POST'])
def login():
  # tok = Token(username='bob')
  # tok.secret = 'shh'
  # tok.encode()
  # tok.update({'username': 'sam'})
  # tok._value = None
  # tok.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QifQ.PbEgFHkDCyWeaxIWTV3Qoo9KREbsUGe2oFbDzyISD1A')
  # print(tok['username'])
  # a = Security()
  # a.token.secret = 'shh'
  # a.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QifQ.PbEgFHkDCyWeaxIWTV3Qoo9KREbsUGe2oFbDzyISD1A'
  # print(a.token)
  print(auth_pages)
  user = None
  if request.method == 'POST':
    user = User.query(User.username == request.form.get('username')).get()
    if user and User.password.verify(request.form.get('password'), user.password):
      set_session(user)
  try:
    return render_template('login.html', auth=None)
  except TemplateNotFound:
    abort(404)
