from services.serve import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now)

    def change_update_time(self) -> "Category":
        self.updated_at = datetime.now()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
