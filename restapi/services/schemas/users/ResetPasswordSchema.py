from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from services.models.UserModel import User

class ResetPasswordSchema(Schema):
    email = fields.Email(required=True,validate=validate.Length(max=100))
    password = fields.Str(required=True,validate=validate.Length(min=6,max=100))
    confirm_password = fields.Str(required=True,validate=validate.Length(min=6,max=100))

    @validates('email')
    def validate_email(self,value):
        if not User.query.filter_by(email=value).first():
            raise ValidationError("We can't find a user with that e-mail address.")

    @validates_schema
    def validate_password_confirm(self,data,**kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError({'password':['Password must match with confirmation.']})
