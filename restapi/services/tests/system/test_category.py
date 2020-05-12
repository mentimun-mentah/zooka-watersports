import json
from basetest import BaseTest
from services.models.UserModel import User
from services.models.CategoryModel import Category

class CategoryTest(BaseTest):
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    EMAIL_TEST = BaseTest.EMAIL_TEST
    EMAIL_TEST_2 = BaseTest.EMAIL_TEST_2
    NAME = 'testtestingtest'
    NAME_2 = 'testingtesttesting'

    def login(self,email: str) -> "CategoryTest":
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

    def register(self,email: str) -> "CategoryTest":
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

    def test_01_validation_create_category(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/category/create',json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)
        # name blank
        with self.app() as client:
            res = client.post('/category/create',json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])

    def test_02_create_category(self):
        with self.app() as client:
            res = client.post('/category/create',json={'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add category.",json.loads(res.data)['message'])

    def test_03_name_already_taken(self):
        with self.app() as client:
            res = client.post('/category/create',json={'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_04_get_category_by_id(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)
        with self.app() as client:
            res = client.get('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # category not found
        with self.app() as client:
            res = client.get('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Category not found",json.loads(res.data)['message'])
        # return category
        category = Category.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/category/crud/{}'.format(category.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn("updated_at",json.loads(res.data).keys())
            self.assertIn("created_at",json.loads(res.data).keys())
            self.assertIn("name",json.loads(res.data).keys())
            self.assertIn("id",json.loads(res.data).keys())

    def test_05_validation_update_category(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.put('/category/crud/9999',json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # category not found
        with self.app() as client:
            res = client.put('/category/crud/9999',json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Category not found",json.loads(res.data)['message'])

        category = Category.query.filter_by(name=self.NAME).first()
        # name blank
        with self.app() as client:
            res = client.put('/category/crud/{}'.format(category.id),json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
        # name already exists
        with self.app() as client:
            res = client.put('/category/crud/{}'.format(category.id),json={'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_06_update_category(self):
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.put('/category/crud/{}'.format(category.id),json={'name': self.NAME_2},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update category.",json.loads(res.data)['message'])

    def test_07_validation_delete_category(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # category not found
        with self.app() as client:
            res = client.delete('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Category not found",json.loads(res.data)['message'])

    def test_08_delete_category(self):
        category = Category.query.filter_by(name=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/category/crud/{}'.format(category.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete category.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
