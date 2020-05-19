from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.models.CommentModel import Comment
from services.models.ActivityModel import Activity
from services.schemas.comments.CommentSchema import CommentSchema
from sqlalchemy import orm

_comment_schema = CommentSchema()

class CreateAndGetCommentActivitiy(Resource):
    def get(self,activity_id: int):
        per_page = request.args.get('per_page',default=None,type=int) or 5
        page = request.args.get('page',default=None,type=int) or 1

        activity = Activity.query.filter_by(id=activity_id).first_or_404('Activity not found')
        comments = Comment.query.options(orm.joinedload('user'),orm.joinedload('replies')).filter(Comment.commentable_type == 'activity',
                Comment.commentable_id == activity.id).paginate(page,per_page,error_out=False)

        result = dict(
            data = _comment_schema.dump(comments.items,many=True),
            next_num = comments.next_num,
            prev_num = comments.prev_num,
            page = comments.page,
            iter_pages = [x for x in comments.iter_pages()]
        )
        return result, 200

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
