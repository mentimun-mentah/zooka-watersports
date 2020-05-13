import os, sys, unittest

_basedir = os.path.join(os.path.dirname(__file__),'../../../')
sys.path.append(_basedir)

from app import app

class BaseTest(unittest.TestCase):
    EMAIL_TEST = "asd@gmail.com"
    EMAIL_TEST_2 = "asd2@gmail.com"

    def setUp(self):
        app.config['JWT_SECRET_KEY'] = 'secretkey'
        self.app = app.test_client
