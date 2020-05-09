import uuid
from services.serve import db
from time import time
from datetime import datetime
from flask import request, url_for
from services.libs.MailSmtp import MailSmtp

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.String(100),primary_key=True)
    email = db.Column(db.String(100),unique=True,index=True,nullable=False)
    resend_expired = db.Column(db.Integer,nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.now)

    def __init__(self,email: str):
        self.email = email
        self.resend_expired = int(time()) + 300  # add 5 minute expired
        self.id = uuid.uuid4().hex

    def send_email_reset_password(self) -> None:
        link = request.url_root[:-1] + url_for('user.reset_password',token=self.id)
        MailSmtp.send_email([self.email],'Reset Password','email/EmailResetPassword.html',link=link)

    @property
    def resend_is_expired(self) -> bool:
        return int(time()) > self.resend_expired

    def change_resend_expired(self) -> "PasswordReset":
        self.resend_expired = int(time()) + 300  # add 5 minute expired

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
