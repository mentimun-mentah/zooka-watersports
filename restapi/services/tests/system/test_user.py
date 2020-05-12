import json, os, io
from time import time
from basetest import BaseTest
from services.models.UserModel import User
from services.models.PasswordResetModel import PasswordReset

class UserTest(BaseTest):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    EMAIL_TEST = BaseTest.EMAIL_TEST
    EMAIL_TEST_2 = BaseTest.EMAIL_TEST_2
    DIR_IMAGE = os.path.join(os.path.dirname(__file__),'../../static/test_image')

    def login(self,email: str) -> "UserTest":
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

    def test_26_validation_add_password(self):
        # login user
        self.login(self.EMAIL_TEST)
        # password and confirm blank
        with self.app() as client:
            res = client.post('/account/add-password',json={'password':'','confirm_password':''},
                headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['password'])
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['confirm_password'])
        # password and confirm not same
        with self.app() as client:
            res = client.post('/account/add-password',json={'password':'asdasd','confirm_password':'asdasdasd'},
                headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Password must match with confirmation."],json.loads(res.data)['password'])

    def test_27_add_password_already_have_password(self):
        # check if user already have password
        with self.app() as client:
            res = client.post('/account/add-password',json={'password':'asdasd','confirm_password':'asdasd'},
                headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertEqual("Your user already have a password",json.loads(res.data)['message'])

    def test_28_add_password_to_user(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.password = None
        user.save_to_db()
        # add new password
        with self.app() as client:
            res = client.post('/account/add-password',json={'password':'asdasd','confirm_password':'asdasd'},
                headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add a password to your account",json.loads(res.data)['message'])

    def test_29_validation_update_password(self):
        # old , password, confirm blank
        with self.app() as client:
            res = client.put('/account/update-password',json={'old_password':'','password':'','confirm_password':''},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['old_password'])
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['password'])
            self.assertListEqual(["Length must be between 6 and 100."],json.loads(res.data)['confirm_password'])
        # password and confirm not same
        with self.app() as client:
            res = client.put('/account/update-password',json={'old_password':'asdasd','password':'asdasd','confirm_password':'asdass'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Password must match with confirmation."],json.loads(res.data)['password'])
        # password doesn't exists in database
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.password = None
        user.save_to_db()

        with self.app() as client:
            res = client.put('/account/update-password',json={'old_password':'asdasd','password':'asdasd','confirm_password':'asdasd'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertEqual("Please add your password first",json.loads(res.data)['message'])

    def test_30_update_password_not_match_in_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.hash_password('asdasd')
        user.save_to_db()
        with self.app() as client:
            res = client.put('/account/update-password',json={'old_password':'asuasu','password':'asdasd','confirm_password':'asdasd'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Password not match with our records'],json.loads(res.data)['old_password'])

    def test_31_update_password_user(self):
        with self.app() as client:
            res = client.put('/account/update-password',json={'old_password':'asdasd','password':'asuasu','confirm_password':'asuasu'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update your password",json.loads(res.data)['message'])

    def test_32_validation_update_account(self):
        # fullname, country, phone blank
        with self.app() as client:
            res = client.put('/account/update-account',json={'fullname':'','country':'','phone':''},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['fullname'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['country'])
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])
        # invalid phone number
        with self.app() as client:
            res = client.put('/account/update-account',json={'fullname':'asdasd','country':2,'phone':'08786233dwq231'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])
        # length phone number between 3 and 20
        with self.app() as client:
            res = client.put('/account/update-account',json={'fullname':'asdasd','country':2,'phone':'87862536363727263632'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 20."],json.loads(res.data)['phone'])
            res = client.put('/account/update-account',json={'fullname':'asdasd','country':2,'phone':'08'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 20."],json.loads(res.data)['phone'])
        # country not found
        with self.app() as client:
            res = client.put('/account/update-account',json={'fullname':'asdasd','country':900,'phone':'08787237464'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Country not found",json.loads(res.data)['message'])

    def test_33_update_account(self):
        with self.app() as client:
            res = client.put('/account/update-account',json={'fullname':'asdasd','country':2,'phone':'08787237464'},
                    headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update your account",json.loads(res.data)['message'])

    def test_34_validation_update_avatar_user(self):
        # avatar not found
        content_type = 'multipart/form-data'
        with self.app() as client:
            res = client.put('/account/update-avatar',content_type=content_type,
                data={'avatar':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['avatar'])
        # danger file extension
        with self.app() as client:
            res = client.put('/account/update-avatar',content_type=content_type,
                data={'avatar': (io.BytesIO(b"print('sa')"), 'test.py')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['avatar'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        # not valid file extension
        with self.app() as client:
            res = client.put('/account/update-avatar',content_type=content_type,
                data={'avatar': (img, 'test.gif')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['avatar'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())

        # file cannot grater than 4 Mb
        with self.app() as client:
            res = client.put('/account/update-avatar',content_type=content_type,
                data={'avatar': (img, 'size.png')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['avatar'])

    def test_35_update_avatar_user(self):
        content_type = 'multipart/form-data'

        with open(os.path.join(self.DIR_IMAGE,'avatar.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/account/update-avatar',content_type=content_type,
                data={'avatar': (img, 'avatar.jpg')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Image profile has updated.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        # delete avatar user
        os.remove(os.path.join(self.DIR_IMAGE,'../avatars/',user.avatar))
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
