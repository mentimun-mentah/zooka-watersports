from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.CategoryModel import Category
from services.schemas.categories.CategorySchema import CategorySchema
from services.schemas.categories.AddImageCategorySchema import AddImageCategorySchema
from services.schemas.categories.UpdateImageCategorySchema import UpdateImageCategorySchema
from services.libs.MagicImage import MagicImage
from services.middleware.Admin import admin_required

_category_schema = CategorySchema()

class CreateCategory(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImageCategorySchema()
        file = _image_schema.load(request.files)
        data = _category_schema.load(request.form)
        # save image
        magic_image = MagicImage(file=file['image'],resize=260,path_upload='categories/')
        magic_image.save_image()
        category = Category(name=data['name'],image=magic_image.FILE_NAME)
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
        _image_schema = UpdateImageCategorySchema()
        file = _image_schema.load(request.files)
        data = _category_schema.load(request.form)
        if file:
            MagicImage.delete_image(file=category.image,path_delete='categories/')
            # save image
            magic_image = MagicImage(file=file['image'],resize=260,path_upload='categories/')
            magic_image.save_image()
            category.image = magic_image.FILE_NAME

        category.name = data['name']
        category.change_update_time()
        category.save_to_db()
        return {"message":"Success update category."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        category = Category.query.filter_by(id=id).first_or_404('Category not found')
        MagicImage.delete_image(file=category.image,path_delete='categories/')
        category.delete_from_db()
        return {"message":"Success delete category."}, 200

class AllCategory(Resource):
    def get(self):
        categories = Category.query.all()
        return _category_schema.dump(categories,many=True), 200
