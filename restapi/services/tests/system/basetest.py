import os, sys, unittest

_basedir = os.path.join(os.path.dirname(__file__),'../../../')
sys.path.append(_basedir)

from app import app

class BaseTest(unittest.TestCase):
    def setUp(self):
        app.config['JWT_SECRET_KEY'] = 'secretkey'
        app.config['ACCESS_TOKEN_EXPIRES'] = 900
        app.config['REFRESH_TOKEN_EXPIRES'] = 2592000
        app.config['SMTP_SERVER'] = 'smtp.gmail.com'
        app.config['SMTP_PORT'] = 465
        app.config['SMTP_USE_SSL'] = True
        app.config['SMTP_EMAIL'] = 'zookatest@gmail.com'
        app.config['SMTP_PASSWORD'] = 'zooka2020'
        self.app = app.test_client
