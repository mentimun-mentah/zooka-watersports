from marshmallow import Schema, fields, validate, validates, ValidationError
from services.models.CategoryModel import Category
from services.models.ActivityModel import Activity

class AddActivitySchema(Schema):
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    description = fields.Str(required=True,validate=validate.Length(min=3))
    duration = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    category = fields.Int(required=True)
    discount = fields.Int()
    price = fields.Int(required=True)
    min_person = fields.Int(required=True)
    include = fields.Str(required=True,validate=validate.Length(min=3))
    pickup = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    information = fields.Str(required=True,validate=validate.Length(min=3))

    @validates('category')
    def validate_category(self,value):
        if not Category.query.get(value):
            raise ValidationError('Category not found')

    @validates('name')
    def validate_name(self,value):
        if Activity.query.filter_by(name=value).first():
            raise ValidationError('The name has already been taken.')
