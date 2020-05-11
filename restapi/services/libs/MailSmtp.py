import os, smtplib
from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

class MailSmtpException(Exception):
    def __init__(self,message: str):
        super().__init__(message)

class MailSmtp:
    _SMTP_SERVER = os.getenv("SMTP_SERVER")
    _PORT = os.getenv("SMTP_PORT")
    _EMAIL = os.getenv("SMTP_EMAIL")
    _PASSWORD = os.getenv("SMTP_PASSWORD")
    _USE_SSL = os.getenv("SMTP_USE_SSL")

    @classmethod
    def send_email(cls,email: List,subject: str,html: str,**param) -> None:
        if not cls._EMAIL: raise MailSmtpException('Email for sender not found')
        if not cls._PASSWORD: raise MailSmtpException('Password for email not found')

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = 'dont-reply'
        msg['To'] = ','.join(email)
        html = render_template(html,**param)

        msg.attach(MIMEText(html,'html'))
        # Try to log in to server smtp
        try:
            if cls._USE_SSL == 'True': server = smtplib.SMTP_SSL(cls._SMTP_SERVER,cls._PORT)
            else: server = smtplib.SMTP(cls._SMTP_SERVER,cls._PORT)
        except smtplib.SMTPException as e:
            raise MailSmtpException(e)

        # login and send email
        try:
            server.login(cls._EMAIL,cls._PASSWORD)
            server.sendmail(cls._EMAIL,email,msg.as_string())
            server.quit()
        except smtplib.SMTPException as e:
            raise MailSmtpException(e)
