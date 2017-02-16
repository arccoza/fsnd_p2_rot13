from flask import Flask, g, Blueprint, current_app, request, make_response, render_template, redirect, url_for, abort
from jinja2 import TemplateNotFound
from models.auth import User
from utils.security import Security, Security2


auth_pages = Blueprint('auth', __name__, template_folder='views')


# sec = SecurityProxy(auth_pages, 'shh')
s2 = Security2(auth_pages, 'shh')


sec = Security()
@auth_pages.record
def prep(setup_state):
  print('record')
  sec.init(setup_state.app, 'shh')

  # @setup_state.app.before_request
  # def hip():
  #   sec.token['username'] = 'bob'


@auth_pages.route('/signup', methods=['GET', 'POST'])
# @sec.allow(lambda t: not t.get('username'), lambda: redirect(url_for('auth.welcome')))
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
        sec.token = {'username': user.username}
        return redirect(url_for('auth.welcome'))
    except Exception as ex:
      print('bad user')
      print(ex)
  try:
    return render_template('signup.html', auth=user, pass_verified=pass_verified)
  except TemplateNotFound:
    abort(404)


@auth_pages.route('/login', methods=['GET', 'POST'])
# @sec.allow(lambda t: not t.get('username'), lambda: redirect(url_for('auth.welcome')))
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
  user = None
  pass_verified = False
  if request.method == 'POST':
    user = User.query(User.username == request.form.get('username')).get()
    if not user:
      user = User()
      user.fill(username=request.form.get('username'))
    if (user and user.password and
      User.password.verify(request.form.get('password'), user.password)):
      sec.token = {'username': user.username}
      pass_verified = True
      return redirect(url_for('auth.welcome'))
  try:
    return render_template('login.html',
                            auth=user, pass_verified=pass_verified)
  except TemplateNotFound:
    abort(404)


@auth_pages.route('/logout')
# @sec.allow(lambda t: t.get('username'), lambda: redirect(url_for('auth.login')))
def logout():
  sec.token = {}
  return redirect(url_for('auth.login'))


@auth_pages.route('/welcome')
def welcome():
  print(s2.token._value)
  return render_template('welcome.html', username=sec.token.get('username'))
