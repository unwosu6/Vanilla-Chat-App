import requests
import json
from imgurpython import ImgurClient
import os


def upload_img(image):
    IMAGES = os.path.join('static', 'images')
    f = open(f'{IMAGES}/{image}', "rb")
    print(IMAGES)
    image_data = f.read()
    url = 'https://api.imgur.com/3/upload.json'
    url2 = 'https://api.imgur.com/3/image/'
    Client_ID = '3c83e1ceb493e23'
    Client_ID2 = '6d379c81402e737'
    secret = '535971c9b0314c3ca5e0a3b56507697bd2ae0afc'
    client = ImgurClient(Client_ID2, secret)
    imgur = client.upload_from_path(
        f'{IMAGES}/{image}', config=None, anon=True)
    imgur_link = imgur['link']
    print(image)
    if os.path.exists(f'{IMAGES}/{image}'):
        os.remove(f'{IMAGES}/{image}')
    else:
        print("The file does not exist")
    return imgur_link
