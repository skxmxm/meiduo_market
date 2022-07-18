from django.urls import path
from apps.areas.views import *

urlpatterns = [
    path('areas/', GetProvince.as_view()),
    path('areas/<province_id>/', GetCity.as_view()),

]