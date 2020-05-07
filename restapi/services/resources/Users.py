from flask_restful import Resource, request
from services.models.ConfirmationModel import Confirmation
from services.models.UserModel import User
from services.schemas.users.RegisterSchema import RegisterSchema
from services.libs.MailSmtp import MailSmtpException

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
