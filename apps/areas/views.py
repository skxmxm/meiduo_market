import json

from django.views import View
from apps.areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache

# Create your views here.
class GetProvince(View):
    def get(self, request):
        provinces_list = cache.get("provinces")
        if provinces_list is None:
            provinces = Area.objects.filter(parent=None)
            provinces_list = []
            for i in provinces:
                provinces_list.append({
                    'id': i.id,
                    'name': i.name,

                })
            cache.set("provinces", provinces_list, 86400)
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': provinces_list})


class GetCity(View):
    def get(self, request, province_id):
        cities_list = cache.get(province_id)
        if cities_list is None:
            cities = Area.objects.get(id=province_id).subs.all()
            cities_list = []
            for i in cities:
                cities_list.append({
                    'id': i.id,
                    'name': i.name,
                })
            cache.set(province_id, cities_list, 86400)
        data = {'subs': cities_list}
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': data})


