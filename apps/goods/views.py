from django.shortcuts import render

# Create your views here.

from utils.minio_client import *
file = open("C:/Users/HJX/Desktop/1.gif", "rb")
minio_upload(file, "1.gif")
