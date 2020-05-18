from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.models.CommentModel import Comment
from services.models.ActivityModel import Activity
from services.schemas.comments.CommentSchema import CommentSchema

_comment_schema = CommentSchema()

class CreateCommentActivitiy(Resource):
    @jwt_required
    def post(self,activity_id: int):
        activity = Activity.query.filter_by(id=activity_id).first_or_404('Activity not found')
        data = request.get_json()
        args = _comment_schema.load(data)
        comment = Comment(args['subject'],activity.id,'activity',get_jwt_identity())
        comment.save_to_db()
        return {"message":"Comment success added"}, 201

class DeleteCommentActivity(Resource):
    @jwt_required
    def delete(self,id: int):
        comment = Comment.query.filter(Comment.commentable_type == 'activity',
                Comment.id == id).first_or_404('Comment not found')
        if comment.user_id != get_jwt_identity():
            return {"message":"You can't delete comment other person"}, 400

        comment.delete_from_db()
        return {"message":"Comment success deleted"}, 200

class GetAllCommentActivity(Resource):
    def get(self,activity_id: int):
        pass
