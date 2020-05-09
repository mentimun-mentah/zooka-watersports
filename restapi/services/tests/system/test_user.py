import json
from basetest import BaseTest
from time import time
from services.models.UserModel import User
from services.models.PasswordResetModel import PasswordReset

class UserTest(BaseTest):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    EMAIL_TEST = "asd@gmail.com"
    EMAIL_TEST_2 = "asd2@gmail.com"

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
                'email': self.EMAIL_TEST,'password':'asdasd',
                'confirm_password':'asdasdasd','terms':True})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Password must match with confirmation."],json.loads(res.data)['password'])

        # check terms doesn't check
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email': self.EMAIL_TEST,'password':'asdasd',
                'confirm_password':'asdasd','terms':False})
            self.assertEqual(400,res.status_code)
            self.assertEqual(["Terms must be checked."],json.loads(res.data)['terms'])

    def test_01_register_new_user(self):
        # register user asd
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email': self.EMAIL_TEST,'password':'asdasd',
                'confirm_password':'asdasd','terms':True})
        self.assertEqual(201,res.status_code)
        self.assertEqual('Check your email to activated user.',json.loads(res.data)['message'])

        # email already exits
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email': self.EMAIL_TEST,'password':'asdasd',
                'confirm_password':'asdasd','terms':True})
        self.assertEqual(400,res.status_code)
        self.assertListEqual(['The email has already been taken.'],json.loads(res.data)['email'])

    def test_02_invalid_token_email(self):
        # token not found
        with self.app() as client:
            res = client.put('/user-confirm/ngawur')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Token not found",json.loads(res.data)['message'])

    def test_03_confirm_email(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        # email activated
        with self.app() as client:
            res = client.put('/user-confirm/{}'.format(user.confirmation.id))
            self.assertEqual(200,res.status_code)
            self.assertEqual(f'Your email {user.email} has been activated',json.loads(res.data)['message'])

    def test_04_email_already_activated(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        # email already activated
        with self.app() as client:
            res = client.put('/user-confirm/{}'.format(user.confirmation.id))
            self.assertEqual(200,res.status_code)
            self.assertEqual("Your account already activated.",json.loads(res.data)['message'])

        # set token expired
        user.confirmation.activated = False
        user.confirmation.expired_at = int(time()) - 1800  # reduce 30 minute
        user.confirmation.save_to_db()

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
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        with self.app() as client:
            res = client.post('/resend-email',json={'email': user.email})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Email confirmation has send',json.loads(res.data)['message'])

    def test_07_check_attempt_to_resen_email_back(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        # check try again 5 minute later
        with self.app() as client:
            res = client.post('/resend-email',json={'email': user.email})
            self.assertEqual(400,res.status_code)
            self.assertEqual('You can try 5 minute later',json.loads(res.data)['message'])

    def test_08_resend_email_already_activated(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
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
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        # invalid credential
        with self.app() as client:
            res = client.post('/login',json={'email': user.email,'password':'asdassadsdd'})
            self.assertEqual(422,res.status_code)
            self.assertEqual('Invalid credential',json.loads(res.data)['message'])

    def test_11_login_user_email_not_activated(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.confirmation.activated = False
        user.confirmation.save_to_db()

        with self.app() as client:
            res = client.post('/login',json={'email': user.email,'password':'asdasd'})
            self.assertEqual(400,res.status_code)
            self.assertEqual('Check your email to activated user.',json.loads(res.data)['message'])

    def test_12_user_login(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
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

    def test_16_validation_send_email_reset_password(self):
        # email blank & invalid format email
        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])
            res = client.post('/send-password/reset',json={'email':'asd@gsad'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])
        # email not found in database
        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':'sadgpge@gmail.com'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["We can't find a user with that e-mail address."],json.loads(res.data)['email'])
        # set user not activated
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.confirmation.activated = False
        user.confirmation.save_to_db()

    def test_17_send_email_reset_not_activated(self):
        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':self.EMAIL_TEST})
            self.assertEqual(400,res.status_code)
            self.assertEqual("Please activated you're user first",json.loads(res.data)['message'])

    def test_18_email_reset_password_not_in_database(self):
        # set user activated
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.confirmation.activated = True
        user.confirmation.save_to_db()

        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':self.EMAIL_TEST})
            self.assertEqual(200,res.status_code)
            self.assertEqual("We have e-mailed your password reset link!",json.loads(res.data)['message'])

    def test_19_wait_5_minute_email_reset(self):
        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':self.EMAIL_TEST})
            self.assertEqual(400,res.status_code)
            self.assertEqual("You can try 5 minute later",json.loads(res.data)['message'])

    def test_20_email_reset_password_in_database(self):
        password_reset = PasswordReset.query.filter_by(email=self.EMAIL_TEST).first()
        password_reset.resend_expired = int(time()) - 300  # reduce 5 minute
        password_reset.save_to_db()
        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':self.EMAIL_TEST})
            self.assertEqual(200,res.status_code)
            self.assertEqual("We have e-mailed your password reset link!",json.loads(res.data)['message'])
        # wait 5 minute
        with self.app() as client:
            res = client.post('/send-password/reset',json={'email':self.EMAIL_TEST})
            self.assertEqual(400,res.status_code)
            self.assertEqual("You can try 5 minute later",json.loads(res.data)['message'])

    def test_21_validation_reset_password(self):
        # email, password, confirm blank
        with self.app() as client:
            res = client.put('/password/reset/token',json={'email':'','password':'','confirm_password':''})
            self.assertEqual(400,res.status_code)
            self.assertIn('email',json.loads(res.data).keys())
            self.assertIn('password',json.loads(res.data).keys())
            self.assertIn('confirm_password',json.loads(res.data).keys())
        # invalid format email
        with self.app() as client:
            res = client.put('/password/reset/token',json={'email':'asd@fad','password':'','confirm_password':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid email address."],json.loads(res.data)['email'])
        #  password and confirm not same
        with self.app() as client:
            res = client.put('/password/reset/token',json={'email':self.EMAIL_TEST,'password':'asdasd','confirm_password':'asdasddd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Password must match with confirmation."],json.loads(res.data)['password'])
        # email not found in database
        with self.app() as client:
            res = client.put('/password/reset/token',json={'email':'asd23sad@gmail.com','password':'','confirm_password':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["We can't find a user with that e-mail address."],json.loads(res.data)['email'])

    def test_22_token_not_found_reset_password(self):
        with self.app() as client:
            res = client.put('/password/reset/tokenngawur',json={'email':self.EMAIL_TEST,'password':'asdasd','confirm_password':'asdasd'})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Token not found",json.loads(res.data)['message'])

    def test_23_add_new_user(self):
        # register user asd2
        with self.app() as client:
            res = client.post('/register',json={'name':'asd',
                'email': self.EMAIL_TEST_2,'password':'asdasd',
                'confirm_password':'asdasd','terms':True})
        self.assertEqual(201,res.status_code)
        self.assertEqual('Check your email to activated user.',json.loads(res.data)['message'])

    def test_24_token_email_not_match_reset_password(self):
        password_reset = PasswordReset.query.filter_by(email=self.EMAIL_TEST).first()
        with self.app() as client:
            res = client.put('/password/reset/{}'.format(password_reset.id),json={'email':self.EMAIL_TEST_2,
                'password':'asdasd',
                'confirm_password':'asdasd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['This password reset token is invalid.'],json.loads(res.data)['email'])

    def test_25_reset_password(self):
        password_reset = PasswordReset.query.filter_by(email=self.EMAIL_TEST).first()
        with self.app() as client:
            res = client.put('/password/reset/{}'.format(password_reset.id),json={'email':self.EMAIL_TEST,
                'password':'asdasd',
                'confirm_password':'asdasd'})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Successfully reset your password",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
