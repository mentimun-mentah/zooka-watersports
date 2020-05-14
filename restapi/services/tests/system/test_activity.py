import json, io, os
from basetest import BaseTest
from services.models.UserModel import User
from services.models.ActivityModel import Activity
from services.models.CategoryModel import Category

class ActivityTest(BaseTest):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    EMAIL_TEST = BaseTest.EMAIL_TEST
    EMAIL_TEST_2 = BaseTest.EMAIL_TEST_2
    NAME = 'testtestingtest'
    NAME_2 = 'testingtesttesting'
    DIR_IMAGE = os.path.join(os.path.dirname(__file__),'../../static/test_image')

    def login(self,email: str) -> "ActivityTest":
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

    def register(self,email: str) -> "ActivityTest":
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

    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST)
        self.register(self.EMAIL_TEST_2)

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_create_category(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        with self.app() as client:
            res = client.post('/category/create',json={'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add category.",json.loads(res.data)['message'])

    def test_02_validation_upload_image_create_activity(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.post('/activity/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        content_type = 'multipart/form-data'
        # check image is required
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':'','image2':'','image3':'','image4':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Missing data for required field."],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # check image2,3,4 is nullable
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg')})
            self.assertEqual(400,res.status_code)
            self.assertNotIn('image2',json.loads(res.data).keys())
            self.assertNotIn('image3',json.loads(res.data).keys())
            self.assertNotIn('image4',json.loads(res.data).keys())
        # check dangerous file
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(io.BytesIO(b"print('sa')"), 'test.py'),
                    'image2': (io.BytesIO(b"print('sa')"), 'test.py'),
                    'image3': (io.BytesIO(b"print('sa')"), 'test.py'),
                    'image4': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image2'])
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image3'])
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image4'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img4 = io.BytesIO(im.read())

        # check file extension
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'test.gif'),
                    'image2': (img2, 'test.gif'),
                    'image3': (img3, 'test.gif'),
                    'image4': (img4, 'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image2'])
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image3'])
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image4'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img4 = io.BytesIO(im.read())

        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'size.png'),
                    'image2': (img2, 'size.png'),
                    'image3': (img3, 'size.png'),
                    'image4': (img4, 'size.png')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image'])
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image2'])
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image3'])
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image4'])

    def test_03_validation_create_activity(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        content_type = 'multipart/form-data'
        # check if name,description,duration,category,discount,price,min_person,include,pickup,information blank
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name':'','description':'','duration':'','category_id':'','discount':'','price':'','min_person':'',
                    'include':'','pickup':'','information':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Shorter than minimum length 3."],json.loads(res.data)['description'])
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['duration'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['category_id'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['discount'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['price'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['min_person'])
            self.assertListEqual(["Shorter than minimum length 3."],json.loads(res.data)['include'])
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['pickup'])
            self.assertListEqual(["Shorter than minimum length 3."],json.loads(res.data)['information'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        # check category not found
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name':'','description':'','duration':'','category_id':9999,'discount':'','price':'','min_person':'',
                    'include':'','pickup':'','information':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Category not found"],json.loads(res.data)['category_id'])

    def test_04_create_activity(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        content_type = 'multipart/form-data'
        category = Category.query.filter_by(name=self.NAME).first()
        # success add activity
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name': self.NAME,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add activity.",json.loads(res.data)['message'])

    def test_05_create_activity_name_already_exists(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        content_type = 'multipart/form-data'
        category = Category.query.filter_by(name=self.NAME).first()
        # check name already taken
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name': self.NAME,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_06_validation_upload_image_update_activity(self):
        self.login(self.EMAIL_TEST_2)
        activity = Activity.query.filter_by(name=self.NAME).first()
        # check user is admin
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        content_type = 'multipart/form-data'

        # check image,image2,3,4 can be null
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={})
            self.assertEqual(400,res.status_code)
            self.assertNotIn('image',json.loads(res.data).keys())
            self.assertNotIn('image2',json.loads(res.data).keys())
            self.assertNotIn('image3',json.loads(res.data).keys())
            self.assertNotIn('image4',json.loads(res.data).keys())
        # check dangerous file
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(io.BytesIO(b"print('sa')"), 'test.py'),
                    'image2': (io.BytesIO(b"print('sa')"), 'test.py'),
                    'image3': (io.BytesIO(b"print('sa')"), 'test.py'),
                    'image4': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image2'])
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image3'])
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image4'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img4 = io.BytesIO(im.read())

        # check file extension
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'test.gif'),
                    'image2': (img2, 'test.gif'),
                    'image3': (img3, 'test.gif'),
                    'image4': (img4, 'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image2'])
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image3'])
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image4'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img4 = io.BytesIO(im.read())

        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'size.png'),
                    'image2': (img2, 'size.png'),
                    'image3': (img3, 'size.png'),
                    'image4': (img4, 'size.png')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image'])
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image2'])
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image3'])
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image4'])

    def test_07_validation_update_activity(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        content_type = 'multipart/form-data'
        # check acitivity not found
        with self.app() as client:
            res = client.put('/activity/crud/99999',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Activity not found",json.loads(res.data)['message'])
        # check if name,description,duration,category,discount,price,min_person,include,pickup,information blank
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'name':'','description':'','duration':'','category_id':'','discount':'','price':'','min_person':'',
                    'include':'','pickup':'','information':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Shorter than minimum length 3."],json.loads(res.data)['description'])
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['duration'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['category_id'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['discount'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['price'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['min_person'])
            self.assertListEqual(["Shorter than minimum length 3."],json.loads(res.data)['include'])
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['pickup'])
            self.assertListEqual(["Shorter than minimum length 3."],json.loads(res.data)['information'])
        # check category not found
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'name':'','description':'','duration':'','category_id':99999,'discount':'','price':'','min_person':'',
                    'include':'','pickup':'','information':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Category not found"],json.loads(res.data)['category_id'])

    def test_08_update_activity(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        content_type = 'multipart/form-data'
        category = Category.query.filter_by(name=self.NAME).first()
        activity = Activity.query.filter_by(name=self.NAME).first()
        # success add activity
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name': self.NAME,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update activity.",json.loads(res.data)['message'])

    def test_09_create_another_activity(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())

        content_type = 'multipart/form-data'
        category = Category.query.filter_by(name=self.NAME).first()
        # success add activity
        with self.app() as client:
            res = client.post('/activity/create',content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img, 'image.jpg'),'image2': (img2, 'image.jpg'),'image3': (img3, 'image.jpg'),'image4': (img4, 'image.jpg'),
                    'name': self.NAME_2,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add activity.",json.loads(res.data)['message'])

    def test_10_can_update_name_if_same_with_previous_activity(self):
        content_type = 'multipart/form-data'
        category = Category.query.filter_by(name=self.NAME).first()
        activity = Activity.query.filter_by(name=self.NAME).first()

        # activity can update name if name is same with previous
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'name': self.NAME,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update activity.",json.loads(res.data)['message'])

    def test_11_update_activity_name_already_exists(self):
        content_type = 'multipart/form-data'
        category = Category.query.filter_by(name=self.NAME).first()
        activity = Activity.query.filter_by(name=self.NAME).first()

        # activity can't update name if name already exists and name is not same with the previous
        with self.app() as client:
            res = client.put('/activity/crud/{}'.format(activity.id),content_type=content_type,headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'name': self.NAME_2,'description':'asds','duration':'dwqwdq',
                    'category_id':category.id,'discount':20,'price':10000,'min_person':2,
                    'include':'dwqdwq','pickup':'dwqdwq','information':'dwqdwq'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_12_get_activity_by_id(self):
        self.login(self.EMAIL_TEST_2)

        activity = Activity.query.filter_by(name=self.NAME).first()
        # check user is admin
        with self.app() as client:
            res = client.get('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # activity not found
        with self.app() as client:
            res = client.get('/activity/crud/99999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Activity not found",json.loads(res.data)['message'])
        # get specific activity
        with self.app() as client:
            res = client.get('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn('id',json.loads(res.data).keys())
            self.assertIn('name',json.loads(res.data).keys())
            self.assertIn('slug',json.loads(res.data).keys())
            self.assertIn('price',json.loads(res.data).keys())
            self.assertIn('discount',json.loads(res.data).keys())
            self.assertIn('min_person',json.loads(res.data).keys())
            self.assertIn('image',json.loads(res.data).keys())
            self.assertIn('image2',json.loads(res.data).keys())
            self.assertIn('image3',json.loads(res.data).keys())
            self.assertIn('image4',json.loads(res.data).keys())
            self.assertIn('description',json.loads(res.data).keys())
            self.assertIn('duration',json.loads(res.data).keys())
            self.assertIn('include',json.loads(res.data).keys())
            self.assertIn('pickup',json.loads(res.data).keys())
            self.assertIn('information',json.loads(res.data).keys())
            self.assertIn('created_at',json.loads(res.data).keys())
            self.assertIn('updated_at',json.loads(res.data).keys())
            self.assertIn('category_id',json.loads(res.data).keys())

    def test_13_get_activity_by_slug(self):
        # note this endpoint is public data
        # activity not found
        with self.app() as client:
            res = client.get('/activity/dwq-dwq-fffqs-wdf')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Activity not found",json.loads(res.data)['message'])

        activity = Activity.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/activity/{}'.format(activity.slug))
            self.assertEqual(200,res.status_code)
            self.assertIn('id',json.loads(res.data).keys())
            self.assertIn('name',json.loads(res.data).keys())
            self.assertIn('slug',json.loads(res.data).keys())
            self.assertIn('price',json.loads(res.data).keys())
            self.assertIn('discount',json.loads(res.data).keys())
            self.assertIn('min_person',json.loads(res.data).keys())
            self.assertIn('image',json.loads(res.data).keys())
            self.assertIn('image2',json.loads(res.data).keys())
            self.assertIn('image3',json.loads(res.data).keys())
            self.assertIn('image4',json.loads(res.data).keys())
            self.assertIn('description',json.loads(res.data).keys())
            self.assertIn('duration',json.loads(res.data).keys())
            self.assertIn('include',json.loads(res.data).keys())
            self.assertIn('pickup',json.loads(res.data).keys())
            self.assertIn('information',json.loads(res.data).keys())
            self.assertIn('created_at',json.loads(res.data).keys())
            self.assertIn('updated_at',json.loads(res.data).keys())
            self.assertIn('category_id',json.loads(res.data).keys())

    def test_14_get_all_activity(self):
        with self.app() as client:
            res = client.get('/activities')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual({},json.loads(res.data))

    def test_15_delete_activity_one(self):
        self.login(self.EMAIL_TEST_2)

        activity = Activity.query.filter_by(name=self.NAME).first()
        # check user is admin
        with self.app() as client:
            res = client.delete('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # check activity not found
        with self.app() as client:
            res = client.delete('/activity/crud/99999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Activity not found",json.loads(res.data)['message'])

        with self.app() as client:
            res = client.delete('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete activity.",json.loads(res.data)['message'])

    def test_16_delete_activity_two(self):
        # check activity not found
        with self.app() as client:
            res = client.delete('/activity/crud/99999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Activity not found",json.loads(res.data)['message'])

        activity = Activity.query.filter_by(name=self.NAME_2).first()
        with self.app() as client:
            res = client.delete('/activity/crud/{}'.format(activity.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete activity.",json.loads(res.data)['message'])

    def test_99_delete_user_and_category_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
        category = Category.query.filter_by(name=self.NAME).first()
        category.delete_from_db()
