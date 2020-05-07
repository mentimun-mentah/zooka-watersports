from services.serve import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    fullname = db.Column(db.String(100),nullable=True)
    phone = db.Column(db.String(20),nullable=True)
    email = db.Column(db.String(100),unique=True,index=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)
    terms = db.Column(db.Boolean,default=False)
    role = db.Column(db.Integer,default=1)
    avatar = db.Column(db.String(100),default='default.png')
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now)

    confirmation = db.relationship('Confirmation',backref='user',uselist=False,cascade='all,delete-orphan')

    def __init__(self,**args):
        self.name = args['name']
        self.email = args['email']
        self.password = bcrypt.generate_password_hash(args['password']).decode("utf-8")
        self.terms = args['terms']

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
