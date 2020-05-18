import re
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity
from services.models.ActivityModel import Activity
from services.models.VisitModel import Visit
from services.models.WishlistModel import Wishlist
from services.schemas.activities.UpdateImageActivitySchema import UpdateImageActivitySchema
from services.schemas.activities.AddImageActivitySchema import AddImageActivitySchema
from services.schemas.activities.ActivitySchema import ActivitySchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage
from marshmallow import ValidationError

_activity_schema = ActivitySchema()

class CreateActivity(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImageActivitySchema()
        files = _image_schema.load(request.files)
        data = _activity_schema.load(request.form)
        if Activity.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        magic_image = MagicImage(file=files,resize=550,path_upload='activities/')
        magic_image.save_image()
        files_name = magic_image.FILE_NAME

        args = {**files_name,**data}
        activity = Activity(**args)
        activity.save_to_db()
        return {"message":"Success add activity."}, 201

class UpdateDeleteActivity(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        activity = Activity.query.filter_by(id=id).first_or_404('Activity not found')
        return _activity_schema.dump(activity), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        activity = Activity.query.filter_by(id=id).first_or_404('Activity not found')
        _image_schema = UpdateImageActivitySchema()
        files = _image_schema.load(request.files)
        data = _activity_schema.load(request.form)
        if activity.name != data['name'] and Activity.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        files_name = dict()
        if files:
            # delete image if exists
            for index in files.keys():
                if index == 'image':
                    MagicImage.delete_image(file=activity.image,path_delete='activities/')
                if index == 'image2':
                    MagicImage.delete_image(file=activity.image2,path_delete='activities/')
                if index == 'image3':
                    MagicImage.delete_image(file=activity.image3,path_delete='activities/')
                if index == 'image4':
                    MagicImage.delete_image(file=activity.image4,path_delete='activities/')
            # save image
            magic_image = MagicImage(file=files,resize=550,path_upload='activities/')
            magic_image.save_image()
            files_name = magic_image.FILE_NAME

        # update data in database
        args = {**files_name,**data}
        activity.update_data_in_db(**args)
        activity.change_update_time()
        activity.save_to_db()
        return {"message":"Success update activity."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        activity = Activity.query.filter_by(id=id).first_or_404('Activity not found')
        files = [activity.image,activity.image2,activity.image3,activity.image4]
        # delete all image in storage
        [MagicImage.delete_image(file=file,path_delete='activities/') for file in files]
        activity.delete_from_db()
        return {"message":"Success delete activity."}, 200

class AllActivities(Resource):
    @jwt_optional
    def get(self):
        _activity_card_schema = ActivitySchema(exclude=("min_person","information","image2","image3","image4","description","duration",
                                                "pickup","include","created_at","updated_at","category"))

        current_user = get_jwt_identity()
        per_page = request.args.get('per_page',default=None,type=int) or 8
        page = request.args.get('page',default=None,type=int) or 1
        q = re.escape(request.args.get('q',default=None,type=str) or '')
        sort = request.args.get('sort',default=None,type=str)
        if q:
            activities = Activity.query.filter(Activity.name.like('%' + q + '%')).paginate(page,per_page,error_out=False)
        elif sort in ['cheap','expensive']:
            if sort == 'cheap':
                activities = Activity.query.order_by(Activity.price.asc()).paginate(page,per_page,error_out=False)
            elif sort == 'expensive':
                activities = Activity.query.order_by(Activity.price.desc()).paginate(page,per_page,error_out=False)
        else:
            activities = Activity.query.paginate(page,per_page,error_out=False)

        # if user login extract data and show wishlist on card
        data = _activity_card_schema.dump(activities.items,many=True)
        if current_user:
            for activity in data:
                if Wishlist.check_wishlist(activity['id'],current_user):
                    activity['love'] = True
                else:
                    activity['love'] = False

        result = dict(
            data = data,
            next_num = activities.next_num,
            prev_num = activities.prev_num,
            page = activities.page,
            iter_pages = [x for x in activities.iter_pages()]
        )
        return result, 200

class GetActivitySlug(Resource):
    def get(self,slug: str):
        activity = Activity.query.filter_by(slug=slug).first_or_404('Activity not found')
        Visit.set_visit(ip=request.remote_addr,visitable_id=activity.id,visitable_type='view_activity')
        data = _activity_schema.dump(activity)
        # get wishlist & seen data
        seen = Visit.get_seen_activity(visit_type='view_activity',visit_id=activity.id)
        wishlist = Wishlist.query.filter_by(activity_id=activity.id).count()
        data['seen'] = seen
        data['wishlist'] = wishlist
        return data, 200

class GetActivitiesMostView(Resource):
    @jwt_optional
    def get(self):
        _activity_card_schema = ActivitySchema(exclude=("min_person","information","image2","image3","image4","description","duration",
                                                "pickup","include","created_at","updated_at","category"))

        current_user = get_jwt_identity()
        visits = Visit.visit_popular_by(visit_type='view_activity',limit=5)
        raw_activity = [Activity.query.get(index) for index,value in visits]
        # if user login extract data and show wishlist on card
        data = _activity_card_schema.dump(raw_activity,many=True)
        if current_user:
            for activity in data:
                if Wishlist.check_wishlist(activity['id'],current_user):
                    activity['love'] = True
                else:
                    activity['love'] = False

        return data, 200

class SearchActivitiesByName(Resource):
    def get(self):
        _activity_name_schema = ActivitySchema(only=("name",))
        q = re.escape(request.args.get('q',default=None,type=str) or '')
        if q:
            activities = Activity.query.filter(Activity.name.like('%' + q + '%')).limit(5).all()
        else:
            activities = []

        return _activity_name_schema.dump(activities,many=True), 200

class ClickActivityBySearchName(Resource):
    def post(self,id: int):
        activity = Activity.query.filter_by(id=id).first_or_404('Activity not found')
        Visit.set_visit(ip=request.remote_addr,visitable_id=activity.id,visitable_type='search_activity')
        return {"message":"Activity by name clicked."}, 200

class GetActivitiesPopularSearch(Resource):
    def get(self):
        _activity_name_schema = ActivitySchema(only=("name",))
        visits = Visit.visit_popular_by(visit_type='search_activity',limit=6)
        raw_activity = [Activity.query.get(index) for index,value in visits]
        return _activity_name_schema.dump(raw_activity,many=True), 200
