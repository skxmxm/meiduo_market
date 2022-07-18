from django.core.mail import send_mail
from celery_handler.main import app
from utils.email_verify_token import generate_token


@app.task
def send_email(to_email, user_id):
    from_email = '美多商城<hjx13576154277@163.com>'
    email_title = '美多商城邮箱激活'
    token = generate_token(user_id)
    url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % token
    html_body = '<p>尊敬的用户您好!</p>' \
                '<p>感谢您使用美多商城。</p>' \
                '<p>您的邮箱为:%s。 请点击此链接激活您的邮箱: </p>' \
                '<p><a href="%s">%s<a></p>' % (to_email, url, url)
    recipient_list = [to_email]
    status = send_mail(from_email=from_email,
                       message='',
                       subject=email_title,
                       recipient_list=recipient_list,
                       html_message=html_body)
    return status
