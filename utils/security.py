from jose import jwt
from functools import wraps
from flask import g, current_app, request


class Token(dict):
  def __init__(self, secret, algorithm='HS256'):
    super(Token, self).__init__()
    self.secret = secret
    self.algorithm = algorithm
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

  def clear(self):
    super(Token, self).clear()
    self._value = None

  # TODO: Make this safer.
  def reset(self, val):
    val.__iter__
    super(Token, self).clear()
    self.update(val)
    # self._value = None

  def encode(self, empty=None):
    # Be cautious here, this only works because `_value` is cleared on updates.
    if not self._value and len(self):
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
  def __init__(self, app=None, id='session'):
    self.req = request
    self._ck = None
    self.id = id
    if app:
      app.after_request(self._set)

  def get(self):
    return self.req.cookies.get(self.id)

  def set(self, token):
    self._ck = {'key': self.id, 'value': token, 'path': '/'}

  def _set(self, res):
    if self._ck:
      res.set_cookie(**self._ck)
    return res

  def rem(self):
    self._ck = {'key': self.id, 'value': '', 'expires': 0, 'path': '/'}


# class Security(object):
#   def init(self, app, secret):
#     self._app = app
#     self._req = request
#     self._token = Token(secret)
#     self._session = Session()
#     app.before_request(self._before)
#     app.after_request(self._after)

#   def _before(self):
#     # print('self._app')
#     if self.session:
#       self.token = self.session

#   def _after(self, res):
#     self.session = self.token.encode()
#     self._session._set(res)
#     return res

#   @property
#   def token(self):
#     return self._token

#   @token.setter
#   def token(self, v):
#     try:
#       self._token.decode(v)
#     except:
#       try:
#         self._token.reset(v)
#       except:
#         self._token.reset({})

#   @property
#   def session(self):
#     return self._session.get()

#   @session.setter
#   def session(self, v):
#     if v:
#       self._session.set(v)
#     else:
#       self._session.rem()

#   def allow(self, cmp, alt=None):
#     def allow_deco(fn):
#       @wraps(fn)
#       def allow_handler(*args, **kwargs):
#         if cmp(self.token):
#           return fn(*args, **kwargs)
#         elif alt:
#           return alt(*args, **kwargs)
#         else:
#           return abort(403)
#       return allow_handler
#     return allow_deco


class Security(object):
  def __init__(self, app, secret):
    def _before():
      g._security = g.get('_security') or {'_token': Token(secret), '_session': Session()}
      if self.session:
        self.token = self.session

    def _after(res):
      self.session = self.token.encode()
      self._session._set(res)
      return res

    app.before_request(_before)
    app.after_request(_after)

  def __getattr__(self, k):
    return g._security[k]

  def __setattr__(self, k, v):
    try:
      self.__class__.__dict__[k].__set__(self, v)
    except Exception as e:
      g._security[k] = v

  @property
  def token(self):
    return self._token

  @token.setter
  def token(self, v):
    try:
      self._token.decode(v)
    except:
      try:
        self._token.reset(v)
      except:
        self._token.reset({})

  @property
  def session(self):
    return self._session.get()

  @session.setter
  def session(self, v):
    if v:
      self._session.set(v)
    else:
      self._session.rem()

  def allow(self, cmp, alt=None):
    def allow_deco(fn):
      @wraps(fn)
      def allow_handler(*args, **kwargs):
        if cmp(self.token):
          return fn(*args, **kwargs)
        elif alt:
          return alt(*args, **kwargs)
        else:
          return abort(403)
      return allow_handler
    return allow_deco


# class SecurityProxy(object):
#   def __init__(self, app, secret):
#     # g._security = g._security or {'inst': Security(app, secret), 'SECRET': secret}
#     def _bp(setup_state):
#       _hooks(setup_state.app)

#     def _hooks(app):
#       with app.app_context():
#         g.security = Security()
#         g.security.init(app, 'shh')
#         print('---------------', g.get('security'))
#       print('---------------', g.get('security'))
#       # app.before_request(_before)
#       # app.after_request(_after)

#     # def _before():
#     #   g.security = Security()
#     #   g.security.init(app, 'shh')

#     # def _after(res):
#     #   return res

#     try:
#       app.record(_bp)
#     except AttributeError as ex:
#       _hooks(app)

#   @property
#   def token(self):
#     print('---------------', g.get('security'))
#     return g.security.token

#   @token.setter
#   def token(self, v):
#     g.security.token = v

#   @property
#   def session(self):
#     return g.security.session

#   @session.setter
#   def session(self, v):
#     g.security.session = v

#   def allow(self, cmp, alt=None):
#     return g.security.allow(cmp, alt)

#   # def _bp(self, setup_state):
#   #   self._hooks(setup_state.app)

#   # def _hooks(self, app):
#   #   app.before_request(self._before)
#   #   app.after_request(self._after)

#   # def _before(self):
#   #   # g.security = Security(current_app)
#   #   pass

#   # def _after(self, res):
#   #   print(current_app)
#   #   return res
