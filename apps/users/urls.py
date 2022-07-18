from django.urls import path, register_converter, converters
from apps.users.views import *
from utils.converters import *
register_converter(UsernameConverter, "username")
register_converter(MobileConverter, "mobile")

urlpatterns = [
    path('usernames/<username:username>/count/', CheckUsername.as_view()),
    path('mobiles/<mobile:mobile>/count/', CheckMobile.as_view()),
    path('register/', register),
    path('login/', user_login),
    path('logout/', user_logout),
    path('info/', UserCenter.as_view()),
    path('emails/', EmailSave.as_view()),
    path('emails/verification/', VerifyEmail.as_view()),
    path('addresses/create/', CreateAddress.as_view()),
    path('addresses/', GetAddress.as_view()),
    path('addresses/<int:address_id>/default/', SetDefaultAddress.as_view()),
    path('addresses/<int:address_id>/', AlterAddress.as_view()),
    path('addresses/<int:address_id>/title/', AlterTitle.as_view()),
]