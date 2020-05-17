from marshmallow import Schema, fields, validate, validates, ValidationError
from services.models.CategoryModel import Category

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    image = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('name')
    def validate_name(self,value):
        if Category.query.filter_by(name=value).first():
            raise ValidationError('The name has already been taken.')
