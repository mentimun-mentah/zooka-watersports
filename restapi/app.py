from services.serve import api, app
from services.libs import OAuth2
from services.resources import Users, Categories, Activities, Wishlists, Comments

api.add_resource(Users.RegisterUser,'/register')
api.add_resource(Users.ConfirmEmail,'/user-confirm/<token>',endpoint='user.confirm')
api.add_resource(Users.ResendEmail,'/resend-email')
api.add_resource(Users.LoginUser,'/login')
api.add_resource(Users.RefreshToken,'/refresh')
api.add_resource(Users.AccessTokenRevoke,'/access_revoke')
api.add_resource(Users.RefreshTokenRevoke,'/refresh_revoke')
api.add_resource(Users.SendPasswordReset,'/send-password/reset')
api.add_resource(Users.ResetPassword,'/password/reset/<token>',endpoint='user.reset_password')

api.add_resource(OAuth2.GoogleLogin,'/login/google')
api.add_resource(OAuth2.GoogleAuthorize,'/login/google/authorized')
api.add_resource(OAuth2.FacebookLogin,'/login/facebook')
api.add_resource(OAuth2.FacebookAuthorize,'/login/facebook/authorized')

api.add_resource(Users.AddPassword,'/account/add-password')
api.add_resource(Users.UpdatePassword,'/account/update-password')
api.add_resource(Users.UpdateAccount,'/account/update-account')
api.add_resource(Users.UpdateAvatar,'/account/update-avatar')

api.add_resource(Categories.AllCategory,'/categories')
api.add_resource(Categories.CreateCategory,'/category/create')
api.add_resource(Categories.UpdateDeleteCategory,'/category/crud/<int:id>')

api.add_resource(Activities.AllActivities,'/activities')
api.add_resource(Activities.GetActivitiesMostView,'/activities/most-viewed')
api.add_resource(Activities.GetActivitiesPopularSearch,'/activities/popular-search')
api.add_resource(Activities.SearchActivitiesByName,'/activities/search-by-name')
api.add_resource(Activities.ClickActivityBySearchName,'/activity/search-by-name/click/<int:id>')
api.add_resource(Activities.GetActivitySlug,'/activity/<slug>')
api.add_resource(Activities.CreateActivity,'/activity/create')
api.add_resource(Activities.UpdateDeleteActivity,'/activity/crud/<int:id>')

api.add_resource(Wishlists.LoveActivity,'/wishlist/love/<int:activity_id>')
api.add_resource(Wishlists.UnloveActivity,'/wishlist/unlove/<int:activity_id>')

api.add_resource(Comments.CreateCommentActivitiy,'/comment/activity/<int:activity_id>')
api.add_resource(Comments.DeleteCommentActivity,'/comment/activity/<int:id>')

if __name__ == '__main__':
    app.run()
