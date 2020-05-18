from services.serve import db
from datetime import datetime

class Wishlist(db.Model):
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer,primary_key=True)
    activity_id = db.Column(db.Integer,db.ForeignKey('activities.id'),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)

    @classmethod
    def check_wishlist(cls,activity: int, user: int) -> "Wishlist":
        return cls.query.filter(cls.activity_id == activity, cls.user_id == user).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
