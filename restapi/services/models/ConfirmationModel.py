import uuid
from time import time
from services.serve import db
from flask import request, url_for
from services.libs.MailSmtp import MailSmtp

class Confirmation(db.Model):
    __tablename__ = 'confirmation_users'

    id = db.Column(db.String(100),primary_key=True)
    activated = db.Column(db.Boolean,default=False)
    resend_expired = db.Column(db.Integer,nullable=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

    def __init__(self,user_id: int):
        self.id = uuid.uuid4().hex
        self.user_id = user_id

    def send_email_confirm(self) -> None:
        link = request.url_root[:-1] + url_for('user.confirm',token=self.id)
        MailSmtp.send_email([self.user.email],'Activated User','email/EmailConfirm.html',link=link,username=self.user.name)

    @property
    def resend_is_expired(self) -> bool:
        return int(time()) > self.resend_expired

    def generate_resend_expired(self) -> "Confirmation":
        self.resend_expired = int(time()) + 300  # add 5 minute

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
