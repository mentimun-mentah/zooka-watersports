from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class UpdatePasswordSchema(Schema):
    old_password = fields.Str(required=True,validate=validate.Length(min=6,max=100))
    password = fields.Str(required=True,validate=validate.Length(min=6,max=100))
    confirm_password = fields.Str(required=True,validate=validate.Length(min=6,max=100))

    @validates_schema
    def validate_password_confirm(self,data,**kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError({'password':['Password must match with confirmation.']})
