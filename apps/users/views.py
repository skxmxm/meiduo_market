import json
import re
from django.shortcuts import render
from apps.users.models import *
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection
from django.contrib.auth import login, logout
from utils.views import LoginRequiredJsonMixin


# Create your views here.
class CheckUsername(View):

    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        return JsonResponse({'count': count})


class CheckMobile(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({'count': count})


def register(request):
    json_data = request.body.decode()
    data = json.loads(json_data)
    username = data.get('username')
    password = data.get('password')
    password2 = data.get('password2')
    mobile = data.get('mobile')
    sms = data.get('sms_code')
    allow = data.get('allow')

    redis_cli = get_redis_connection('captcha')
    real_sms = redis_cli.get(mobile).decode()

    if not all([username, password, password2, mobile, sms, allow]):
        return JsonResponse({'code': 400, 'errmsg': 'found empty data'})
    elif not re.match('[0-9a-zA-Z_-]{5,20}', username):
        return JsonResponse({'code': 400, 'errmsg': 'username is invalid'})
    elif User.objects.filter(username=username).count():
        return JsonResponse({'code': 400, 'errmsg': 'username is used'})
    elif not re.match(r'[0-9a-zA-Z_-]{8,20}', password) or not re.match(r'[0-9a-zA-Z_-]{8,20}', password2):
        return JsonResponse({'code': 400, 'errmsg': 'password is invalid'})
    elif password != password2:
        return JsonResponse({'code': 400, 'errmsg': 'passwords are different'})
    elif not re.match(r'^1[345789]\d{9}$', mobile):
        return JsonResponse({'code': 400, 'errmsg': 'mobile number is invalid'})
    elif User.objects.filter(mobile=mobile).count():
        return JsonResponse({'code': 400, 'errmsg': 'mobile number is used'})
    elif not allow:
        return JsonResponse({'code': 400, 'errmsg': 'certificate is not allowed'})
    elif real_sms is None:
        return JsonResponse({'code': 400, 'errmsg': 'sms_code does not exist'})
    elif sms != real_sms:
        return JsonResponse({'code': 400, 'errmsg': 'sms_code is not pairing'})
    else:
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        login(request, user)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', username)
        return response


def user_login(request):
    user_data = json.loads(request.body.decode())
    name = user_data.get('username')
    password = user_data.get('password')
    remembered = user_data.get('remembered')

    if not all([name, password]):
        return JsonResponse({'code': 400, 'errmsg': "missing arguments"})

    if re.match(r'1[3-9]\d{9}', name):
        User.USERNAME_FIELD = 'mobile'
    else:
        User.USERNAME_FIELD = 'username'

    from django.contrib.auth import authenticate
    user = authenticate(username=name, password=password)

    if user is None:
        return JsonResponse({'code': 400, 'errmsg': "用户名或密码错误"})

    login(request, user)

    if remembered:
        # 默认两周
        request.session.set_expiry(None)

    else:
        # 直到浏览器关闭
        request.session.set_expiry(0)

    response = JsonResponse({'code': 0, 'errmsg': "ok"})
    response.set_cookie('username', user.username, expires=1209600)
    return response


def user_logout(request):
    logout(request)

    response = JsonResponse({'code': 0, 'errmsg': "ok"})
    response.delete_cookie('username')
    return response


class EmailSave(LoginRequiredJsonMixin, View):

    def put(self, request):
        data = json.loads(request.body.decode())
        email = data.get('email')
        if not re.match(r'^[a-z\d][\w.-]*@[a-z\d-]+(.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400, 'errmsg': '邮箱格式错误'})
        user = request.user
        user.email = email
        user.save()
        # 发送激活邮件
        from celery_handler.email.tasks import send_email
        send_email.delay(email, user.id)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class UserCenter(LoginRequiredJsonMixin, View):

    def get(self, request):
        data = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        response = JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': data})
        return response


class VerifyEmail(View):
    def put(self, request):
        token = request.GET.get('token')

        if token is None:
            return JsonResponse({'code': 400, 'errmsg': 'token missing'})
        from utils.email_verify_token import verify_token
        data = verify_token(token)
        if data['code'] != 0:
            return JsonResponse({'code': 400, 'errmsg': 'wrong token'})
        else:
            user_id = data['id']
            user = User.objects.get(id=user_id)
            user.email_active = True
            user.save()
            return JsonResponse({'code': 0, 'errmsg': 'ok'})


class CreateAddress(LoginRequiredJsonMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        user = request.user
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400, 'errmsg': 'missing necessary arguments'})
        if not re.match(r"1[3-9]\d{9}", mobile):
            return JsonResponse({'code': 400, 'errmsg': 'wrong mobile'})
        if tel:
            if not re.match(r'^(0\d{2,3}-)?([2-9]\d{6,7})+(-\d{1,4})?$', tel):
                return JsonResponse({'code': 400, 'errmsg': 'wrong tel'})
        if email:
            if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(.[a-zA-Z0-9_-]+)+$', email):
                return JsonResponse({'code': 400, 'errmsg': 'wrong email'})

        try:
            new_address = Address.objects.create(
                user=user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            return JsonResponse({'code': 401, 'errmsg': 'server error'})
        else:
            address = {
                'id': new_address.id,
                'title': new_address.receiver,
                'receiver': new_address.receiver,
                'province': new_address.province.name,
                'city': new_address.city.name,
                'district': new_address.district.name,
                'place': new_address.place,
                'mobile': new_address.mobile,
                'tel': new_address.tel,
                'email': new_address.email,
            }
            return JsonResponse(
                {'code': 0, 'errmsg': 'ok', 'address': address, 'default_address_id': user.default_address_id})


class GetAddress(LoginRequiredJsonMixin, View):
    def get(self, request):
        user = request.user
        address = Address.objects.filter(user=user, is_deleted=False)
        address_list = []
        for i in address:
            address_list.append({
                'id': i.id,
                'title': i.receiver,
                'receiver': i.receiver,
                'province': i.province.name,
                'city': i.city.name,
                'district': i.district.name,
                'place': i.place,
                'mobile': i.mobile,
                'tel': i.tel,
                'email': i.email,
            })
        return JsonResponse(
            {'code': 0, 'errmsg': 'ok', 'addresses': address_list, 'default_address_id': user.default_address_id})


class SetDefaultAddress(LoginRequiredJsonMixin, View):
    def put(self, request, address_id):
        user = request.user
        address = Address.objects.filter(user=user, is_deleted=False)
        have_address = False
        for i in address:
            if i.id == address_id:
                have_address = True
                break
        if not have_address:
            return JsonResponse({'code': 400, 'errmsg': 'address not found'})
        user.default_address_id = address_id
        user.save()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class AlterAddress(LoginRequiredJsonMixin, View):
    def delete(self, request, address_id):
        user = request.user
        address = Address.objects.filter(user=user, is_deleted=False)
        have_address = False
        for i in address:
            if i.id == address_id:
                if i.user.default_address_id == address_id:
                    user.default_address_id = None
                i.is_deleted = True
                have_address = True
                user.save()
                i.save()
                break
        if not have_address:
            return JsonResponse({'code': 400, 'errmsg': '该地址已被删除，请尝试刷新页面'})
        else:
            return JsonResponse({'code': 0, 'errmsg': 'ok'})

    def put(self, request, address_id):
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        address = Address.objects.get(id=address_id)
        if address is None:
            return JsonResponse({'code': 400, 'errmsg': '该地址不存在，请尝试刷新页面'})
        address.receiver = receiver
        address.province_id = province_id
        address.city_id = city_id
        address.district_id = district_id
        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email
        address.save()

        address_dict = {
            'id': address_id,
            'title': address.title,
            'receiver': receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': place,
            'mobile': mobile,
            'tel': tel,
            'email': email,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'address': address_dict})


class AlterTitle(LoginRequiredJsonMixin, View):
    def put(self, request, address_id):
        user = request.user
        title = json.loads(request.body.decode()).get('title')
        address = Address.objects.filter(user=user, is_deleted=False)
        have_address = False
        for i in address:
            if i.id == address_id:
                have_address = True
                i.title = title
                i.save()
                break
        if not have_address:
            return JsonResponse({'code': 400, 'errmsg': 'address not found'})
        else:
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
