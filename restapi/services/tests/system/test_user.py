import json
from basetest import BaseTest
from time import time
from services.models.UserModel import User

class UserTest(BaseTest):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None

    def test_00_validation_register(self):
        # all field blank
        with self.app() as client:
            res = client.post('/register',json={'name':'',
                'email':'','password':'',
                'confirm_password':'','terms':''})
            self.assertEqual(400,res.status_code)
            self.assertIn('name',json.loads(res.data).keys())
            self.assertIn('email',json.loads(res.data).keys())
            self.assertIn('password',json.loads(res.data).keys())
            self.assertIn('confirm_password',json.loads(res.data).keys())
            self.assertIn('terms',json.loads(res.data).keys())

        # check valid email
        with self.app() as client:
            res = client.post('/register',json={'email':'asdsd@asd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])

        # check length name, password, confirm_password & not valid boolean terms
        with self.app() as client:
            res = client.post('/register',json={'name':'a','password':'a','confirm_password':'a','terms':'a'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['password'])
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['confirm_password'])
            self.assertListEqual(["Not a valid boolean."],json.loads(res.data)['terms'])

        # check password with confirm password
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email':'asd@gmail.com','password':'asdasd',
                'confirm_password':'asdasdasd','terms':True})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Password must match with confirmation."],json.loads(res.data)['password'])

        # check terms doesn't check
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email':'asd@gmail.com','password':'asdasd',
                'confirm_password':'asdasd','terms':False})
            self.assertEqual(400,res.status_code)
            self.assertEqual(["Terms must be checked."],json.loads(res.data)['terms'])

    def test_01_register_new_user(self):
        # register user asd
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email':'asd@gmail.com','password':'asdasd',
                'confirm_password':'asdasd','terms':True})
        self.assertEqual(201,res.status_code)
        self.assertEqual('Check your email to activated user.',json.loads(res.data)['message'])

        # email already exits
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email':'asd@gmail.com','password':'asdasd',
                'confirm_password':'asdasd','terms':True})
        self.assertEqual(400,res.status_code)
        self.assertListEqual(['The email has already been taken.'],json.loads(res.data)['email'])

    def test_03_invalid_token_email(self):
        # token not found
        with self.app() as client:
            res = client.get('/user-confirm/ngawur')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Token not found",json.loads(res.data)['message'])

    def test_02_confirm_email(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        # email activated
        with self.app() as client:
            res = client.get('/user-confirm/{}'.format(user.confirmation.id))
            self.assertEqual(200,res.status_code)
            self.assertEqual(f'Your email {user.email} has been activated',json.loads(res.data)['message'])

    def test_03_email_already_activated(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        # email already activated
        with self.app() as client:
            res = client.get('/user-confirm/{}'.format(user.confirmation.id))
            self.assertEqual(200,res.status_code)
            self.assertEqual("Your account already activated.",json.loads(res.data)['message'])

        # set token expired
        user.confirmation.activated = False
        user.confirmation.expired_at = int(time()) - 1800  # reduce 30 minute
        user.confirmation.save_to_db()

    def test_04_token_email_expired(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        with self.app() as client:
            res = client.get('/user-confirm/{}'.format(user.confirmation.id))
            self.assertEqual(400,res.status_code)
            self.assertEqual("Upps token expired, you can resend email confirm again",json.loads(res.data)['message'])

    def test_05_validation_resend_email_confirm(self):
        # check email blank, invalid format, email not found
        with self.app() as client:
            res = client.post('/resend-email',json={'email':''})
            self.assertEqual(400,res.status_code)
            res = client.post('/resend-email',json={'email':'dwq@ad'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])
            res = client.post('/resend-email',json={'email':'dqwqwwdw@gmail.com'})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Email not found.',json.loads(res.data)['message'])

    def test_06_resend_email_confirm(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        with self.app() as client:
            res = client.post('/resend-email',json={'email': user.email})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Email confirmation has send',json.loads(res.data)['message'])

    def test_07_check_attempt_to_resen_email_back(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        # check try again 5 minute later
        with self.app() as client:
            res = client.post('/resend-email',json={'email': user.email})
            self.assertEqual(400,res.status_code)
            self.assertEqual('You can try 5 minute later',json.loads(res.data)['message'])

    def test_08_resend_email_already_activated(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        user.confirmation.activated = True
        user.confirmation.save_to_db()
        with self.app() as client:
            res = client.post('/resend-email',json={'email': user.email})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Your account already activated.',json.loads(res.data)['message'])

    def test_09_validation_login_user(self):
        # email & password blank
        with self.app() as client:
            res = client.post('/login',json={'email':'','password':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['password'])
        # email format
        with self.app() as client:
            res = client.post('/login',json={'email':'asdd@gmasd','password':'asdasd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])

    def test_10_login_user_invalid_credential(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        # invalid credential
        with self.app() as client:
            res = client.post('/login',json={'email': user.email,'password':'asdassadsdd'})
            self.assertEqual(422,res.status_code)
            self.assertEqual('Invalid credential',json.loads(res.data)['message'])

    def test_11_login_user_email_not_activated(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        user.confirmation.activated = False
        user.confirmation.save_to_db()

        with self.app() as client:
            res = client.post('/login',json={'email': user.email,'password':'asdasd'})
            self.assertEqual(400,res.status_code)
            self.assertEqual('Check your email to activated user.',json.loads(res.data)['message'])

    def test_12_user_login(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        user.confirmation.activated = True
        user.confirmation.save_to_db()

        with self.app() as client:
            # get access token and refresh token
            res = client.post('/login',json={"email": user.email,"password":"asdasd"})
            self.assertEqual(200,res.status_code)
            self.assertIn('access_token',json.loads(res.data).keys())
            self.assertIn('refresh_token',json.loads(res.data).keys())
            self.assertIn('name',json.loads(res.data).keys())
            self.__class__.ACCESS_TOKEN = json.loads(res.data)['access_token']
            self.__class__.REFRESH_TOKEN = json.loads(res.data)['refresh_token']

    def test_13_refresh_token(self):
        with self.app() as client:
            res = client.post('/refresh',headers={'Authorization':f'Bearer {self.REFRESH_TOKEN}'})
            self.assertEqual(200,res.status_code)
            self.assertIn('access_token',json.loads(res.data).keys())

    def test_14_revoke_access_token(self):
        with self.app() as client:
            res = client.delete('/access_revoke',headers={'Authorization':f'Bearer {self.ACCESS_TOKEN}'})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Access token revoked.',json.loads(res.data)['message'])

    def test_15_revoke_refresh_token(self):
        with self.app() as client:
            res = client.delete('/refresh_revoke',headers={'Authorization':f'Bearer {self.REFRESH_TOKEN}'})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Refresh token revoked.',json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email='asd@gmail.com').first()
        user.delete_from_db()
