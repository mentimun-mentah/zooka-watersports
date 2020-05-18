import json, os, io
from basetest import BaseTest
from services.models.UserModel import User
from services.models.CategoryModel import Category
from services.models.ActivityModel import Activity

class CommentTest(BaseTest):
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

    def test_03_validation_create_comment_activity(self):
        # activity not found
        with self.app() as client:
            res = client.post('/comment/activity/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Activity not found',json.loads(res.data)['message'])

        activity = Activity.query.filter_by(name=self.NAME).first()
        # comment subject blank
        with self.app() as client:
            res = client.post('/comment/activity/{}'.format(activity.id),json={'subject':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Shorter than minimum length 5."],json.loads(res.data)['subject'])

    def test_04_create_comment_activity(self):
        activity = Activity.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.post('/comment/activity/{}'.format(activity.id),json={'subject':'asdasdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual('Comment success added',json.loads(res.data)['message'])

        self.login(self.EMAIL_TEST_2)

    def test_05_validation_delete_comment_activity(self):
        # comment not found
        with self.app() as client:
            res = client.delete('/comment/activity/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Comment not found',json.loads(res.data)['message'])
        # other user delete comment
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        with self.app() as client:
            res = client.delete('/comment/activity/{}'.format(user.comments[0].id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertEqual("You can't delete comment other person",json.loads(res.data)['message'])

    def test_06_delete_comment_activity(self):
        self.login(self.EMAIL_TEST)

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        with self.app() as client:
            res = client.delete('/comment/activity/{}'.format(user.comments[0].id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Comment success deleted",json.loads(res.data)['message'])

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
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
