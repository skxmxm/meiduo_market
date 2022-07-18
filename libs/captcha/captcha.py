import os
import random
import string

from captcha.image import ImageCaptcha


def captcha():
    image = ImageCaptcha()
    charset = string.digits + string.ascii_uppercase
    num = 5
    captcha_str = "".join(random.sample(charset, num))
    captcha_img = image.generate_image(captcha_str)
    captcha_img.save("./libs/captcha/image/" + captcha_str + ".jpg")
    with open("./libs/captcha/image/" + captcha_str + ".jpg", 'rb') as file:
        img_binary = file.read()
    os.remove("./libs/captcha/image/" + captcha_str + ".jpg")
    return captcha_str, img_binary
