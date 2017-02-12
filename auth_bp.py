from flask import Blueprint, request, render_template, redirect, url_for, abort
from jinja2 import TemplateNotFound
from google.appengine.ext import ndb
import re
from collections import namedtuple
from passlib.hash import pbkdf2_sha256 as pw_hasher


Conf = namedtuple('Conf', ['PASSWORD_SECRET'])
conf = Conf('sssshhhhhhhhhhhh!')
auth_pages = Blueprint('auth', __name__, template_folder='views')


def not_empty(prop, v):
  if v:
    return v
  else:
    raise TypeError(s._name + ' cannot be empty.')


_re_is_username = re.compile('^[a-zA-Z0-9_-]{3,20}$')
_re_is_password = re.compile('^.{3,20}$')
_re_is_email = re.compile('^[\S]+@[\S]+.[\S]+$')


def is_username(prop, v):
  if v and _re_is_username.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid username.')


def is_password(prop, v):
  # print('is_password: ', v, _re_is_password.match(v))
  if v and _re_is_password.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid password.')


def is_email(prop, v):
  # print('is_email: ', v, _re_is_email.match(v))
  if v and _re_is_email.match(v):
    return v
  else:
    raise TypeError(prop._name + ' must be a valid email.')


class PasswordProperty(ndb.StringProperty):
  def _validate(self, value):
    if not isinstance(value, (str, unicode)):
      raise TypeError('expected a string, got %s' % repr(value))
    if not pw_hasher.identify(value):
      return pw_hasher.hash(is_password(self, value))

  def verify(cls, password, hash):
    print(password, hash)
    return pw_hasher.verify(password, hash)


class User(ndb.Model):
  username = ndb.StringProperty(required=True, validator=is_username)
  password = PasswordProperty(required=True)
  email = ndb.StringProperty(required=True, validator=is_email)
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)

  def valid(self, prop=None):
    isValid = False
    props = {prop: self._properties.get(prop)} if prop else self._properties
    for k, v in props.iteritems():
      if isinstance(v, ndb.Property):
        try:
          val = self._values.get(k)
          # print(k)
          if v._required and not val:
            # print(k, val, v._required)
            return False
          setattr(self, k, val)
          print(k)
          isValid = True
        except Exception as ex:
          # print(ex)
          return False
    return isValid

  def fill(self, **kwargs):
    print('populate:')
    # for k, v in kwargs.iteritems():
    for k in self._properties:
      v = kwargs.get(k)
      if v:
        self._values[k] = v


@auth_pages.route('/signup/', methods=['GET', 'POST'])
def signup():
  # u = User(username='test', password='1234', email='test@mail.com')
  # u.put()
  # print(u._values)
  user = None
  pass_verified = None
  if request.method == 'POST':
    try:
      user = User()
      user.fill(**request.form.to_dict())
      pass_verified = request.form.get('verify') == request.form.get('password')
      print('---', user.valid('password'))
      if user.valid() and pass_verified:
        user.put()
      print(user._values)
      # print(user.valid())
    except Exception as ex:
      print('bad user')
  try:
    return render_template('signup.html', auth=user, pass_verified=pass_verified)
  except TemplateNotFound:
    abort(404)


@auth_pages.route('/login/', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    pass
  try:
    return render_template('login.html', auth=None)
  except TemplateNotFound:
    abort(404)
