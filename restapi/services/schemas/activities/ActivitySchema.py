from marshmallow import Schema, fields, validate, validates, ValidationError
from services.models.CategoryModel import Category

class ActivitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    slug = fields.Str(dump_only=True)
    description = fields.Str(required=True,validate=validate.Length(min=3))
    duration = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    discount = fields.Int()
    price = fields.Int(required=True)
    min_person = fields.Int(required=True)
    include = fields.Str(required=True,validate=validate.Length(min=3))
    pickup = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    information = fields.Str(required=True,validate=validate.Length(min=3))
    image = fields.Str(dump_only=True)
    image2 = fields.Str(dump_only=True)
    image3 = fields.Str(dump_only=True)
    image4 = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    category_id = fields.Int(required=True)

    @validates('category_id')
    def validate_category_id(self,value):
        if not Category.query.get(value):
            raise ValidationError('Category not found')
