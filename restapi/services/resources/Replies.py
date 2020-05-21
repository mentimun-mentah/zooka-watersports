from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.models.ReplyModel import Reply
from services.models.CommentModel import Comment
from services.schemas.replies.ReplySchema import ReplySchema

_reply_schema = ReplySchema()

class CreateReplyComment(Resource):
    @jwt_required
    def post(self,comment_id: int):
        comment = Comment.query.filter_by(id=comment_id).first_or_404('Comment not found')
        data = request.get_json()
        args = _reply_schema.load(data)
        reply = Reply(args['subject'],comment.id,get_jwt_identity())
        reply.save_to_db()
        return {"message":"Reply success added"}, 201

class DeleteReplyComment(Resource):
    @jwt_required
    def delete(self,id: int):
        reply = Reply.query.filter_by(id=id).first_or_404('Reply not found')
        if reply.user_id != get_jwt_identity():
            return {"message":"You can't delete reply other person"}, 400

        reply.delete_from_db()
        return {"message":"Reply success deleted"}, 200
