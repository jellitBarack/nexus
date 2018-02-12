from app import db

# https://github.com/mitsuhiko/flask-openid/blob/master/example/example.py
class Client(db.Model):
    """
    A client is the app which wants to use the resource of a user. It is suggested that the client is registered
    by a user on your site, but it is not required.

    The client should contain at least these properties:

        client_id: A random string
        client_secret: A random string
        client_type: A string represents if it is confidential
        redirect_uris: A list of redirect uris
        default_redirect_uri: One of the redirect uris
        default_scopes: Default scopes of the client
        But it could be better, if you implemented:

        allowed_grant_types: A list of grant types
        allowed_response_types: A list of response types
        validate_scopes: A function to validate scopes
    """
    # human readable name, not required
    name = db.Column(db.String(40))

    # human readable description, not required
    description = db.Column(db.String(400))

    # creator of the client, not required
    user_id = db.Column(db.ForeignKey('users.id'))
    # required if you need to support client credential
    user = db.relationship('User')

    client_id = db.Column(db.String(50), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True,
                              nullable=False)

    # public or confidential
    is_confidential = db.Column(db.Boolean)

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []
    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))

class Grant(db.Model):
    """
    A grant token is created in the authorization flow, and will be destroyed when the authorization is finished.
    In this case, it would be better to store the data in a cache, which leads to better performance.
    A grant token should contain at least this information:

        client_id: A random string of client_id
        code: A random string
        user: The authorization user
        scopes: A list of scope
        expires: A datetime.datetime in UTC
        redirect_uri: A URI string
        delete: A function to delete itself

    """
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.String(30), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(50), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))

class Token(db.Model):
    """
    A bearer token is the final token that could be used by the client. There are other token types, but bearer token is widely used. Flask-OAuthlib only comes with a bearer token.

    A bearer token requires at least this information:
        access_token: A string token
        refresh_token: A string token
        client_id: ID of the client
        scopes: A list of scopes
        expires: A datetime.datetime object
        user: The user object
        delete: A function to delete itself

    """
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(50), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.String(30), db.ForeignKey('users.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))