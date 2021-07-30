import requests
import json
from imgurpython import ImgurClient
import os


def upload_img(image):
    f = open(f'temp/{image}', "rb")
    image_data = f.read()
    url = 'https://api.imgur.com/3/upload.json'
    url2 = 'https://api.imgur.com/3/image/'
    Client_ID = '3c83e1ceb493e23'
    Client_ID2 = '6d379c81402e737'
    secret = '535971c9b0314c3ca5e0a3b56507697bd2ae0afc'
    client = ImgurClient(Client_ID2, secret)
    imgur = client.upload_from_path(f'temp/{image}', config=None, anon=True)
    imgur_link = imgur['link']
    print(image)
    if os.path.exists(f'temp/{image}'):
        os.remove(f'temp/{image}')
    else:
        print("The file does not exist")
    return imgur_link
