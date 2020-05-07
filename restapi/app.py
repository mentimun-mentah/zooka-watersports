from services.serve import api, app
from services.resources import Users

api.add_resource(Users.RegisterUser,'/register')
api.add_resource(Users.ConfirmUser,'/user-confirm/<token>',endpoint='user.confirm')

if __name__ == '__main__':
    app.run()
