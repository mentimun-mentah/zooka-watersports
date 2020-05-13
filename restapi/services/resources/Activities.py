from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.ActivityModel import Activity
from services.schemas.activities.ImageActivitySchema import ImageActivitySchema
from services.schemas.activities.AddActivitySchema import AddActivitySchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage

class CreateActivity(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = ImageActivitySchema()
        _add_schema = AddActivitySchema()
        files = _image_schema.load(request.files)
        data = _add_schema.load(request.form)

        files_name = dict()
        for index,file in files.items():
            magic_image = MagicImage(file=file,resize=550,path_upload='activities/')
            magic_image.save_image()
            files_name[index] = magic_image.FILE_NAME

        args = {**files_name,**data}
        activity = Activity(**args)
        activity.save_to_db()
        return {"message":"Success add activity."}, 201
