from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.models.WishlistModel import Wishlist
from services.models.ActivityModel import Activity

class LoveActivity(Resource):
    @jwt_required
    def post(self,activity_id: int):
        activity = Activity.query.filter_by(id=activity_id).first_or_404('Activity not found')
        if not Wishlist.check_wishlist(activity.id,get_jwt_identity()):
            wishlist = Wishlist(activity_id=activity.id,user_id=get_jwt_identity())
            wishlist.save_to_db()
            return {"message":"Activity entered into the wishlist"}, 200
        return {"message":"Activity already in wishlist"}, 200

class UnloveActivity(Resource):
    @jwt_required
    def delete(self,activity_id: int):
        activity = Activity.query.filter_by(id=activity_id).first_or_404('Activity not found')
        if (wishlist := Wishlist.check_wishlist(activity.id,get_jwt_identity())):
            wishlist.delete_from_db()
            return {"message":"Activity remove from wishlist"}, 200
        return {"message":"Activity not on wishlist"}, 200
