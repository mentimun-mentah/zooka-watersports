from services.serve import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    fullname = db.Column(db.String(100),nullable=True)
    phone = db.Column(db.String(20),nullable=True)
    email = db.Column(db.String(100),unique=True,index=True,nullable=False)
    password = db.Column(db.String(100),nullable=True)
    terms = db.Column(db.Boolean,default=False)
    role = db.Column(db.Integer,default=1)
    avatar = db.Column(db.String(100),default='default.png')
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now)
    country_id = db.Column(db.Integer,db.ForeignKey('countries.id'),nullable=True)

    confirmation = db.relationship('Confirmation',backref='user',uselist=False,cascade='all,delete-orphan')
    wishlists = db.relationship('Wishlist',backref='user',cascade='all,delete-orphan')
    comments = db.relationship('Comment',backref='user',cascade='all,delete-orphan')

    def __init__(self,**args):
        self.name = args['name']
        self.email = args['email']
        self.terms = args['terms']
        if 'avatar' in args:
            self.avatar = args['avatar']
        if 'password' in args:
            self.password = bcrypt.generate_password_hash(args['password']).decode("utf-8")

    def check_pass(self,password: str) -> bool:
        return bcrypt.check_password_hash(self.password,password)

    def hash_password(self,password: str) -> "User":
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def change_update_time(self) -> "User":
        self.updated_at = datetime.now()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
