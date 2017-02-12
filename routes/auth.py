from flask import Blueprint, request, render_template, redirect, url_for, abort
from jinja2 import TemplateNotFound
from models.auth import User


auth_pages = Blueprint('auth', __name__, template_folder='views')


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
      if user.valid() and pass_verified:
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
  user = None
  if request.method == 'POST':
    user = User.gql('WHERE username = %s' % request.form.get('username'))
    print(user)
  try:
    return render_template('login.html', auth=None)
  except TemplateNotFound:
    abort(404)
