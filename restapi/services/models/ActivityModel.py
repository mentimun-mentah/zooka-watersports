from services.serve import db
from datetime import datetime
from slugify import slugify

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    slug = db.Column(db.Text,unique=True,index=True,nullable=False)
    price = db.Column(db.Integer,nullable=False)
    discount = db.Column(db.Integer,nullable=True)
    min_person = db.Column(db.Integer,nullable=False)
    image = db.Column(db.String(100),nullable=False)
    image2 = db.Column(db.String(100),nullable=True)
    image3 = db.Column(db.String(100),nullable=True)
    image4 = db.Column(db.String(100),nullable=True)
    description = db.Column(db.Text,nullable=False)
    duration = db.Column(db.String(100),nullable=False)
    include = db.Column(db.Text,nullable=False)
    pickup = db.Column(db.String(100),nullable=False)
    information = db.Column(db.Text,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now)

    category_id = db.Column(db.Integer,db.ForeignKey('categories.id'),nullable=False)

    def __init__(self,**data):
        self.name = data['name']
        self.slug = slugify(self.name)
        self.price = data['price']
        self.min_person = data['min_person']
        self.image = data['image']
        self.description = data['description']
        self.duration = data['duration']
        self.include = data['include']
        self.pickup = data['pickup']
        self.information = data['information']
        self.category_id = data['category']

        if 'discount' in data:
            self.discount = data['discount']
        if 'image2' in data:
            self.image2 = data['image2']
        if 'image3' in data:
            self.image3 = data['image3']
        if 'image4' in data:
            self.image4 = data['image4']

    def change_update_time(self) -> "Activity":
        self.updated_at = datetime.now()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
