from flask import Blueprint, request, render_template, redirect, url_for, abort
from jinja2 import TemplateNotFound
from google.appengine.ext import ndb
import re


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
  print('is_password: ', v, _re_is_password.match(v))
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


class User(ndb.Model):
  username = ndb.StringProperty(required=True, validator=is_username)
  password = ndb.StringProperty(required=True, validator=is_password)
  email = ndb.StringProperty(required=True, validator=is_email)
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)

  def valid(self, prop=None):
    isValid = False
    # props = {prop: getattr(User, prop, None)} if prop else vars(User)
    props = {prop: self._properties.get(prop)} if prop else self._properties
    # print(props)
    for k, v in props.iteritems():
      if isinstance(v, ndb.Property):
        # print(k, v)
        try:
          # v._validate(self._values.get(k))
          # print(v)
          # is_username(v, self._values.get(k))
          val = self._values.get(k)
          if not (v._required and val):
            return False
          setattr(self, k, val)
          print(k)
          isValid = True
        except Exception as ex:
          return False
    return isValid

  def populate(self, **kwargs):
    print('populate:')
    for k, v in kwargs.iteritems():
      self._values[k] = v


@auth_pages.route('/signup/', methods=['GET', 'POST'])
def signup():
  # u = User()
  # print('-----------')
  # u._values['username'] = 's'
  # # u.password = None
  # print('-----------')
  # # # print(isinstance(User.username, ndb.Property))
  # print(u)
  # print(u.valid('password'))
  user = None
  if request.method == 'POST':
    try:
      user = User()
      user.populate(**request.form.to_dict())
      print(user)
    except Exception as ex:
      print('bad user')
      # user = None
  try:
    # print('\nuser:')
    # print(user)
    return render_template('signup.html', auth=user)
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
