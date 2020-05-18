from services.serve import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer,primary_key=True)
    subject = db.Column(db.Text,nullable=False)
    commentable_id = db.Column(db.Integer,nullable=False)
    commentable_type = db.Column(db.String(30),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

    def __init__(self,subject: str, commentable_id: int, commentable_type: str, user_id: int):
        self.subject = subject
        self.commentable_id = commentable_id
        self.commentable_type = commentable_type
        self.user_id = user_id

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
