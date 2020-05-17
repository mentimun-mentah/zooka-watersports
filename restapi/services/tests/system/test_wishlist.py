import json, os, io
from basetest import BaseTest
from services.models.UserModel import User
from services.models.CategoryModel import Category
from services.models.ActivityModel import Activity

class WishlistTest(BaseTest):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    EMAIL_TEST = BaseTest.EMAIL_TEST
    NAME = BaseTest.NAME
    DIR_IMAGE = BaseTest.DIR_IMAGE
    content_type = 'multipart/form-data'

    def login(self,email: str) -> "WishlistTest":
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

    def register(self,email: str) -> "WishlistTest":
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

    def test_00_add_user(self):
        self.register(self.EMAIL_TEST)
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())

    def test_01_create_category(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/category/create',content_type=self.content_type,data={'image': (img,'image.jpg'),'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add category.",json.loads(res.data)['message'])

    def test_02_create_activity(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        category = Category.query.filter_by(name=self.NAME).first()
        # success add activity
        with self.app() as client:
            res = client.post('/activity/create',content_type=self.content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name': self.NAME,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add activity.",json.loads(res.data)['message'])

    def test_03_validation_love_activity(self):
        # activity not found
        with self.app() as client:
            res = client.post('/wishlist/love/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Activity not found',json.loads(res.data)['message'])

    def test_04_love_activity(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        # success add activity in wishlist
        with self.app() as client:
            res = client.post('/wishlist/love/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Activity entered into the wishlist',json.loads(res.data)['message'])

    def test_05_love_activity_already_in_wishlist(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        # activity already in wishlist
        with self.app() as client:
            res = client.post('/wishlist/love/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Activity already in wishlist',json.loads(res.data)['message'])

    def test_06_validation_unlove_activity(self):
        # activity not found
        with self.app() as client:
            res = client.delete('/wishlist/unlove/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Activity not found',json.loads(res.data)['message'])

    def test_07_unlove_activity(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        # success remove activity in wishlist
        with self.app() as client:
            res = client.delete('/wishlist/unlove/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Activity remove from wishlist',json.loads(res.data)['message'])

    def test_08_unlove_activity_already_in_wishlist(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        # activity not on wishlist
        with self.app() as client:
            res = client.delete('/wishlist/unlove/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Activity not on wishlist',json.loads(res.data)['message'])

    def test_97_delete_activity(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.delete('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete activity.",json.loads(res.data)['message'])

    def test_98_delete_category(self):
        category = Category.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.delete('/category/crud/{}'.format(category.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete category.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
