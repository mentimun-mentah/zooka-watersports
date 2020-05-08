from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from services.models.UserModel import User

class RegisterSchema(Schema):
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    email = fields.Email(required=True,validate=validate.Length(max=100))
    password = fields.Str(required=True,validate=validate.Length(min=6,max=100))
    confirm_password = fields.Str(required=True,validate=validate.Length(min=6,max=100))
    terms = fields.Boolean(required=True)

    @validates('email')
    def validate_email(self,value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('The email has already been taken.')

    @validates_schema
    def validate_password_confirm(self,data,**kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError({'password':['Password must match with confirmation.']})

    @validates('terms')
    def validate_terms(self,value):
        if not value: raise ValidationError('Terms must be checked.')
