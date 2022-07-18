from django.urls import path, register_converter
from apps.verifications.views import *
from utils.converters import *
register_converter(MobileConverter, 'mobile')

urlpatterns = [
    path('image_codes/<uuid>/', create_captcha),
    path('sms_codes/<mobile:mobile>/', sms_check),
]