from marshmallow import Schema, fields, validate

class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    subject = fields.Str(required=True,validate=validate.Length(min=5))
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested('UserSchema',only=("id","name","avatar",))
    replies = fields.List(fields.Nested('ReplySchema'))
