from services.serve import db
from datetime import datetime

class Reply(db.Model):
    __tablename__ = 'replies'

    id = db.Column(db.Integer,primary_key=True)
    subject = db.Column(db.Text,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    comment_id = db.Column(db.Integer,db.ForeignKey('comments.id'),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

    def __init__(self,subject: str, comment_id: int, user_id: int):
        self.subject = subject
        self.comment_id = comment_id
        self.user_id = user_id

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
