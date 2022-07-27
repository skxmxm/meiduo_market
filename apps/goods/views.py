from django.shortcuts import render
from django.views import View
from utils.goods import *
from apps.contents.models import *
from apps.goods.models import SKU
from django.http import JsonResponse
from haystack.views import SearchView


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


class GoodsList(View):
    def get(self, request, cat_id):
        ordering = request.GET.get('ordering')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        try:
            category = GoodsCategory.objects.get(id=cat_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '不存在此id'})

        breadcrumb = get_breadcrumb(category)

        try:
            skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)
        except:
            return JsonResponse({'code': 400, 'errmsg': '查询失败'})

        from django.core.paginator import Paginator
        p = Paginator(skus, page_size)
        goods_page = p.page(page)

        goods_list = []
        for sku in goods_page.object_list:
            goods_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        total_page = p.num_pages

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'breadcrumb': breadcrumb,
            'list': goods_list,
            'count': total_page
        })


class HotGoods(View):
    def get(self, request, cat_id):
        try:
            category = GoodsCategory.objects.get(id=cat_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '不存在此id'})

        try:
            skus = SKU.objects.filter(category=category, is_launched=True).order_by("-sales")
        except:
            return JsonResponse({'code': 400, 'errmsg': '查询失败'})

        from django.core.paginator import Paginator
        p = Paginator(skus, 5)
        goods_page = p.page(1)

        goods_list = []

        for sku in goods_page.object_list:
            goods_list.append({
                'id': str(sku.id),
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': goods_list})




class SKUSearchView(SearchView):
    def create_response(self):
        context = self.get_context()
        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url
            })
        return JsonResponse(sku_list, safe=False)
