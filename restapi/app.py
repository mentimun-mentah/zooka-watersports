from services.serve import api, app
from services.resources import Users

api.add_resource(Users.RegisterUser,'/register')
api.add_resource(Users.ConfirmEmail,'/user-confirm/<token>',endpoint='user.confirm')
api.add_resource(Users.ResendEmail,'/resend-email')
api.add_resource(Users.LoginUser,'/login')
api.add_resource(Users.RefreshToken,'/refresh')
api.add_resource(Users.AccessTokenRevoke,'/access_revoke')
api.add_resource(Users.RefreshTokenRevoke,'/refresh_revoke')
api.add_resource(Users.SendPasswordReset,'/send-password/reset')
api.add_resource(Users.ResetPassword,'/password/reset/<token>',endpoint='user.reset_password')

if __name__ == '__main__':
    app.run()
