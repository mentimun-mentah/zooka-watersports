from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.CategoryModel import Category
from services.schemas.categories.CategorySchema import CategorySchema
from services.middleware.Admin import admin_required
from marshmallow import ValidationError

_category_schema = CategorySchema()

class CreateCategory(Resource):
    @jwt_required
    @admin_required
    def post(self):
        data = request.get_json()
        args = _category_schema.load(data)
        if Category.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        category = Category(name=args['name'])
        category.save_to_db()
        return {"message":"Success add category."}, 201

class UpdateDeleteCategory(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        category = Category.query.filter_by(id=id).first_or_404('Category not found')
        return _category_schema.dump(category), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        category = Category.query.filter_by(id=id).first_or_404('Category not found')
        data = request.get_json()
        args = _category_schema.load(data)
        # check name already exists
        if Category.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})
        # update time
        category.name = args['name']
        category.change_update_time()
        category.save_to_db()
        return {"message":"Success update category."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        category = Category.query.filter_by(id=id).first_or_404('Category not found')
        category.delete_from_db()
        return {"message":"Success delete category."}, 200

class AllCategory(Resource):
    @jwt_required
    @admin_required
    def get(self):
        categories = Category.query.all()
        return _category_schema.dump(categories,many=True), 200
