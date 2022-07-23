from django.shortcuts import render
from django.views import View
from apps.goods.models import *
from utils.goods import *
from apps.contents.models import *
from utils.minio_client import *


# Create your views here.

class Index(View):
    def get(self, request):
        # 商品
        goods = get_categories()

        # 广告
        contents = {}
        contents_categories = ContentCategory.objects.all()

        for i in contents_categories:
            contents[i.key] = i.content_set.filter(status=True).order_by('sequence')
        context = {
            "contents": contents,
            "categories": goods,
        }

        return render(request, 'index.html', context)