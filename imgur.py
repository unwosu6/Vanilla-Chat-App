import requests
# import urllib2
import urllib
import base64
import json
import urllib.request
import urllib.parse

def upload_img(image):
    f = open(f'temp/{image}', "rb")
    image_data = f.read()
    url = 'https://api.imgur.com/3/upload.json'
    Client_ID = '4d803a728b3e6d9'
    HEADERS = {'Authorization': 'Client-ID ' + Client_ID}
#     FORM = {f'image={image}'}
    data = {'image': image_data, 'title': 'test'} # create a dictionary.
    response = requests.post(url,HEADERS,data)
    json = response.json()
#     request = urllib.request(url=url, data= urllib.parse.urlencode(data),headers=HEADERS)
#     response = urllib.request.urlopen(request).read()
#     parse = json.loads(response)
    return json

