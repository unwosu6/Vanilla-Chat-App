import requests
# import urllib2
import urllib
import base64
import json
import urllib.request
import urllib.parse
from imgurpython import ImgurClient

def upload_img(image):
    f = open(f'temp/{image}', "rb")
    image_data = f.read()
    url = 'https://api.imgur.com/3/upload.json'
    url2 = 'https://api.imgur.com/3/image/'
    Client_ID = '3c83e1ceb493e23'
    Client_ID2= '6d379c81402e737'
    secret = '535971c9b0314c3ca5e0a3b56507697bd2ae0afc'
    client = ImgurClient(Client_ID2, secret)
    image = client.upload_from_path(f'temp/{image}', config=None, anon=True)
    imgur_link = image['link']
    return imgur_link
#     auth = 'https://api.imgur.com/oauth2/authorize?client_id=3c83e1ceb493e23&response_type=token'
#     response = requests.get(auth)
#     return response
#     HEADERS = {'Authorization':'Client-ID ' + Client_ID}
#     headers = {'Authorization': 'Client-ID 6d379c81402e737'}
#     FORM = {f'image={image}'}
#     data = {'image': image_data, 'title': 'test'} # create a dictionary.
#     response = requests.post(url,headers,data)
#     json = response.json()
#     request = urllib.request(url=url, data= urllib.parse.urlencode(data),headers=HEADERS)
#     response = urllib.request.urlopen(request).read()
#     parse = json.loads(response)
#     return json

