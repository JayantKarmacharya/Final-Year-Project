from django.urls import path
from django.contrib.auth import views as auth_views
from UserApp.views import (user_logout, user_login,
                           user_register, userprofile, user_update,
                           user_password, usercomment,
                           comment_delete)

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('profile/', userprofile, name='userprofile'),
    path('user_update/', user_update, name="user_update"),
    path('password_update/', user_password, name="user_password"),
    path('user_comment/', usercomment, name="usercomment"),
    path('user_comment_delete/<int:id>/', comment_delete, name="comment_delete"),


]
