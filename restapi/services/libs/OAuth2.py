import os, uuid
from typing import Dict
from flask import session, redirect
from flask_restful import Resource, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from requests_oauthlib import OAuth2Session, requests
from services.models.UserModel import User
from services.models.ConfirmationModel import Confirmation
from services.serve import conn_redis

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

class CreateToken:
    _ACCESS_EXPIRES = int(os.getenv("ACCESS_TOKEN_EXPIRES"))  # 15 minute
    _REFRESH_EXPIRES = int(os.getenv("REFRESH_TOKEN_EXPIRES"))  # 30 days

    @classmethod
    def get_token(cls,user_id: int) -> Dict[str,str]:
        # create access_token & refresh_token
        access_token = create_access_token(identity=user_id,fresh=True)
        refresh_token = create_refresh_token(identity=user_id)
        # encode jti token to store database redis
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)
        # store to database redis
        conn_redis.set(access_jti, 'false', cls._ACCESS_EXPIRES)
        conn_redis.set(refresh_jti, 'false', cls._REFRESH_EXPIRES)

        return {"access_token": access_token, "refresh_token": refresh_token}

class SaveUser:
    _dir_avatars = os.path.join(os.path.dirname(__file__),'../static/avatars/')

    @classmethod
    def save_user_to_db(cls,**args) -> int:
        resp = requests.get(args['picture'])
        filename = uuid.uuid4().hex + '.jpg'
        file = os.path.join(cls._dir_avatars,filename)
        with open(file,"wb") as f:
            f.write(resp.content)
        user = User(name=args['name'],email=args['email'],terms=True,avatar=filename)
        user.save_to_db()
        confirmation = Confirmation(user.id)
        confirmation.activated = True
        confirmation.save_to_db()

        return user.id

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

        check_user = User.query.filter_by(email=result['email']).first()
        if check_user:
            token = CreateToken.get_token(check_user.id)
            return token

        user_id = SaveUser.save_user_to_db(name=result['name'],
            email=result['email'],
            picture=result['picture'])

        # return access_token & refresh token
        token = CreateToken.get_token(user_id)
        return token

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

        check_user = User.query.filter_by(email=result['email']).first()
        if check_user:
            token = CreateToken.get_token(check_user.id)
            return token

        user_id = SaveUser.save_user_to_db(name=result['name'],
            email=result['email'],
            picture=result['picture']['data']['url'])

        # return access_token & refresh token
        token = CreateToken.get_token(user_id)
        return token
