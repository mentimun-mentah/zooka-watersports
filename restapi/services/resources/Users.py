from flask_restful import Resource, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    get_jti
)
from services.models.ConfirmationModel import Confirmation
from services.models.UserModel import User
from services.schemas.users.RegisterSchema import RegisterSchema
from services.schemas.users.UserSchema import UserSchema
from services.libs.MailSmtp import MailSmtpException
from services.serve import conn_redis

_ACCESS_EXPIRES = 15 * 60  # 15 minute
_REFRESH_EXPIRES = 30 * 86400  # 30 days

class RegisterUser(Resource):
    def post(self):
        _register_schema = RegisterSchema()
        data = request.get_json()
        args = _register_schema.load(data)
        user = User(**args)
        user.save_to_db()
        try:
            confirmation = Confirmation(user.id)
            confirmation.save_to_db()
            confirmation.send_email_confirm()
        except MailSmtpException as err:
            user.delete_from_db()
            return {"error":str(err)}, 500
        return {"message":"Check your email to activated user."}, 201

class ConfirmUser(Resource):
    def get(self,token: str):
        confirmation = Confirmation.query.filter_by(id=token).first_or_404(description='Token not found')
        if confirmation.activated:
            return {"message":"Your account already activated."}, 200

        if not confirmation.token_is_expired:
            confirmation.activated = True
            confirmation.save_to_db()
            return {"message":f"Your email {confirmation.user.email} has been activated"}, 200
        return {"message":"Upps token expired, you can resend email confirm again"}, 400

class ResendEmail(Resource):
    def post(self):
        _user_schema = UserSchema(only=("email",))
        data = request.get_json()
        args = _user_schema.load(data)
        user = User.query.filter_by(email=args['email']).first_or_404(description='Email not found.')
        if user.confirmation.activated:
            return {"message":"Your account already activated."}, 200

        if user.confirmation.resend_expired is None or user.confirmation.resend_is_expired:
            try:
                user.confirmation.send_email_confirm()
                user.confirmation.change_expired()
                user.confirmation.generate_resend_expired()
                user.confirmation.save_to_db()
                return {"message":"Email confirmation has send"}, 200
            except MailSmtpException as err:
                return {"error":str(err)}, 500
        return {"message":"You can try 5 minute later"}, 400

class LoginUser(Resource):
    def post(self):
        _user_schema = UserSchema(only=("email","password",))
        data = request.get_json()
        args = _user_schema.load(data)
        user = User.query.filter_by(email=args['email']).first()
        if user and user.check_pass(args['password']):
            if user.confirmation.activated:
                access_token = create_access_token(identity=user.id,fresh=True)
                refresh_token = create_refresh_token(identity=user.id)
                # encode jti token to store database redis
                access_jti = get_jti(encoded_token=access_token)
                refresh_jti = get_jti(encoded_token=refresh_token)
                # store to database redis
                conn_redis.set(access_jti, 'false', _ACCESS_EXPIRES)
                conn_redis.set(refresh_jti, 'false', _REFRESH_EXPIRES)
                return {"access_token": access_token,"refresh_token": refresh_token,"name": user.name}, 200
            return {"message":"Check your email to activated user."}, 400
        return {"message":"Invalid credential"}, 422

class RefreshToken(Resource):
    @jwt_refresh_token_required
    def post(self):
        user_id = get_jwt_identity()
        new_token = create_access_token(identity=user_id,fresh=False)
        access_jti = get_jti(new_token)
        conn_redis.set(access_jti, 'false', _ACCESS_EXPIRES)
        return {"access_token": new_token}, 200

class AccessTokenRevoke(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        conn_redis.set(jti, 'true', _ACCESS_EXPIRES)
        return {"message":"Access token revoked."}, 200

class RefreshTokenRevoke(Resource):
    @jwt_refresh_token_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        conn_redis.set(jti, 'true', _REFRESH_EXPIRES)
        return {"message":"Refresh token revoked."}, 200
