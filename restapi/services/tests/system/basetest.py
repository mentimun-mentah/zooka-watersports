import os, sys, unittest, json

_basedir = os.path.join(os.path.dirname(__file__),'../../../')
sys.path.append(_basedir)

from app import app
from services.models.UserModel import User

class BaseTest(unittest.TestCase):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    EMAIL_TEST = "asd@gmail.com"
    EMAIL_TEST_2 = "asd2@gmail.com"
    NAME = 'testtestingtest'
    NAME_2 = 'testingtesttesting'
    DIR_IMAGE = os.path.join(_basedir,'services/static/test_image')
    content_type = 'multipart/form-data'

    def setUp(self):
        app.config['JWT_SECRET_KEY'] = 'secretkey'
        self.app = app.test_client

    def login(self,email: str) -> "BaseTest":
        user = User.query.filter_by(email=email).first()

        with self.app() as client:
            # get access token and refresh token
            res = client.post('/login',json={"email": user.email,"password":"asdasd"})
            self.assertEqual(200,res.status_code)
            self.assertIn('access_token',json.loads(res.data).keys())
            self.assertIn('refresh_token',json.loads(res.data).keys())
            self.assertIn('name',json.loads(res.data).keys())
            self.__class__.ACCESS_TOKEN = json.loads(res.data)['access_token']
            self.__class__.REFRESH_TOKEN = json.loads(res.data)['refresh_token']

    def register(self,email: str) -> "BaseTest":
        # register user asd
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email': email,'password':'asdasd',
                'confirm_password':'asdasd','terms':True})
        self.assertEqual(201,res.status_code)
        self.assertEqual('Check your email to activated user.',json.loads(res.data)['message'])

        user = User.query.filter_by(email=email).first()
        user.confirmation.activated = True
        user.confirmation.save_to_db()
