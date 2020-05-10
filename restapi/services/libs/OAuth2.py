import os
from flask import session, redirect
from flask_restful import Resource, request
from requests_oauthlib import OAuth2Session

_GOOGLE_CLIENT_ID = os.getenv("GOOGLE_ID")
_GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_SECRET")
_GOOGLE_AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
_GOOGLE_TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
_GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_URL")
_GOOGLE_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

_FACEBOOK_CLIENT_ID = os.getenv("FB_ID")
_FACBEOOK_CLIENT_SECRET = os.getenv("FB_SECRET")
_FACEBOOK_AUTHORIZATION_BASE_URL = "https://www.facebook.com/v3.3/dialog/oauth"
_FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v3.3/oauth/access_token"
_FACEBOOK_REDIRECT_URI = os.getenv("FB_URL")
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
