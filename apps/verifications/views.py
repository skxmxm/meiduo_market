import random
import string

from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection

from django.views import View


# Create your views here.
def create_captcha(request, uuid):
    from libs.captcha.captcha import captcha
    text, image = captcha()
    from django_redis import get_redis_connection
    connection = get_redis_connection("captcha")
    connection.setex(uuid, 100, text)
    return HttpResponse(image, content_type="image/jpeg")


def sms_check(request, mobile):
    img_data = request.GET
    img_uuid = img_data.get("image_code_id")
    img_content = str(img_data.get("image_code")).lower()
    if not all([img_content, img_uuid]):
        return JsonResponse({'code': 400, 'errmsg': 'missing argument'})

    redis_cli = get_redis_connection('captcha')
    flag = redis_cli.get('flag_%s' % mobile)

    if flag is not None:
        return JsonResponse({'code': 400, 'errmsg': '操作过于频繁'})

    real_content = str(redis_cli.get(img_uuid).decode('utf8')).lower()
    if real_content is None:
        return JsonResponse({'code': 400, 'errmsg': '验证码过期'})

    if real_content != img_content:
        return JsonResponse({'code': 400, 'errmsg': '图形验证码错误'})

    pl = redis_cli.pipeline()

    content = random.sample(string.digits, 6)
    content_str = "".join(content)

    pl.setex("flag_%s" % mobile, 60, 1)
    pl.setex(mobile, 180, content_str)
    pl.execute()

    from celery_handler.sms.tasks import celery_send_sms

    celery_send_sms.delay(mobile, content_str)

    return JsonResponse({'code': 0, 'errmsg': 'ok'})




