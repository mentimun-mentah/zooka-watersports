from marshmallow import Schema, fields, validate

class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    subject = fields.Str(required=True,validate=validate.Length(min=5))
    commentable_id = fields.Int(dump_only=True)
    commentable_type = fields.Str(dump_only=True)
