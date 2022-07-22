import os
from minio import Minio
from minio.error import InvalidResponseError

minio_client = Minio('192.168.31.220:19000', access_key='admin', secret_key='hjx654321', secure=False)


def minio_upload(file_data, file_name):
    try:
        file_data.seek(0, os.SEEK_END)
        size = file_data.tell()
        file_data.seek(0, 0)
        minio_client.put_object('mdfiles', file_name, file_data, size)
    except InvalidResponseError as e:
        print(e)
        return False
    else:
        return True


def minio_download(file_name):
    try:
        file_data = minio_client.get_object('mdfiles', file_name)
    except InvalidResponseError as e:
        print(e)
        return False
    else:
        return file_data
