from marshmallow import Schema, fields, validate, validates, ValidationError

class UpdateAccountSchema(Schema):
    fullname = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    country = fields.Int(required=True)
    phone = fields.Number(required=True)

    @validates('phone')
    def validate_phone(self,value):
        value = str(int(value))
        if len(value) < 3 or len(value) >= 20:
            raise ValidationError("Length must be between 3 and 20.")
