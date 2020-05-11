from services.serve import db

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer,primary_key=True)
    code = db.Column(db.String(2),unique=True,index=True,nullable=False)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)

    users = db.relationship('User',backref='country',cascade='all,delete-orphan')

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
