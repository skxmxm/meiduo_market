from django.urls import path
from apps.goods.views import *

urlpatterns = [
    path('index/', Index.as_view()),
    path('list/<cat_id>/skus/', GoodsList.as_view()),
    path('hot/<cat_id>/', HotGoods.as_view()),
    path('search/', SKUSearchView())
]