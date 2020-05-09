from flask_restful import Resource, request
from flask import session, redirect
from requests_oauthlib import OAuth2Session

_GOOGLE_CLIENT_ID = "1058335432158-krp6d335sk1olhhio0uiur69d6op8803.apps.googleusercontent.com"
_GOOGLE_CLIENT_SECRET = "yNZ5iRQYLDUjnInyLIsnbD85"
_GOOGLE_AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
_GOOGLE_TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
_GOOGLE_REDIRECT_URI = "http://localhost:5000/login/google/authorized"
_GOOGLE_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

_FACEBOOK_CLIENT_ID = "296063704727141"
_FACBEOOK_CLIENT_SECRET = "74e650d0e357391d7298d73f46c2f2e6"
_FACEBOOK_AUTHORIZATION_BASE_URL = "https://www.facebook.com/v3.3/dialog/oauth"
_FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v3.3/oauth/access_token"
_FACEBOOK_REDIRECT_URI = "http://localhost:5000/login/facebook/authorized"
_FACEBOOK_SCOPE = ["email"]

class GoogleLogin(Resource):
    def get(self):
        google = OAuth2Session(_GOOGLE_CLIENT_ID,scope=_GOOGLE_SCOPE,redirect_uri=_GOOGLE_REDIRECT_URI)
        authorization_url, state = google.authorization_url(_GOOGLE_AUTHORIZATION_BASE_URL)
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)

class GoogleAuthorize(Resource):
    def get(self):
        google = OAuth2Session(_GOOGLE_CLIENT_ID, redirect_uri=_GOOGLE_REDIRECT_URI,state=session['oauth_state'])
        google.fetch_token(_GOOGLE_TOKEN_URL, client_secret=_GOOGLE_CLIENT_SECRET,authorization_response=request.url)
        result = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        return result

class FacebookLogin(Resource):
    def get(self):
        facebook = OAuth2Session(_FACEBOOK_CLIENT_ID,scope=_FACEBOOK_SCOPE,redirect_uri=_FACEBOOK_REDIRECT_URI)
        authorization_url, state = facebook.authorization_url(_FACEBOOK_AUTHORIZATION_BASE_URL)
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        return redirect(authorization_url)

class FacebookAuthorize(Resource):
    def get(self):
        facebook = OAuth2Session(_FACEBOOK_CLIENT_ID,redirect_uri=_FACEBOOK_REDIRECT_URI,state=session['oauth_state'])
        facebook.fetch_token(_FACEBOOK_TOKEN_URL,client_secret=_FACBEOOK_CLIENT_SECRET,authorization_response=request.url)
        result = facebook.get('https://graph.facebook.com/me?fields=name,email,picture').json()
        return result
