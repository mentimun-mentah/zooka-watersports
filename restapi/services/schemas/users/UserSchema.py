from marshmallow import Schema, fields, validate

# except role
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    fullname = fields.Str()
    phone = fields.Str()
    email = fields.Email(required=True,validate=validate.Length(max=100))
    password = fields.Str(load_only=True,required=True,validate=validate.Length(min=6,max=100))
    terms = fields.Boolean()
    avatar = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
