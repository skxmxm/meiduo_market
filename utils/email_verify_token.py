from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta


def generate_token(user_id):
    expire = datetime.utcnow() + timedelta(seconds=86400)
    header = {'alg': 'HS256'}
    key = 'django-insecure-^vz)ra_r_7h5_@c#3sa!pzd9_j)_2=$@mf@3=_-la_6!e$m96j'
    data = {'exp': expire, 'id': user_id}
    return jwt.encode(header=header, payload=data, key=key).decode()


def verify_token(token):
    try:
        data = jwt.decode(token, 'django-insecure-^vz)ra_r_7h5_@c#3sa!pzd9_j)_2=$@mf@3=_-la_6!e$m96j')
    except JoseError as e:
        return {'code': 400, "errmsg": '解密出错'}
    else:
        if datetime.fromtimestamp(data['exp']) < datetime.now():
            return {'code': 401, 'errmsg': '超时'}
        else:
            return {'code': 0, 'errmsg': 'ok', 'id': data['id']}
