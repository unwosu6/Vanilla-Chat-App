#import requests
# import urllib2
import urllib
import base64
import json
import urllib.request
import urllib.parse

def upload_img(image):
#     f = open(image, "rb")
    url = 'https://api.imgur.com/3/image'
    Client_ID = '4d803a728b3e6d9'
    HEADERS = {'Authorization': 'Client-ID ' + Client_ID}
#     FORM = {f'image={image}'}
    data = {'image': image, 'title': 'test'} # create a dictionary.
    request = urllib.request(url="https://api.imgur.com/3/upload.json", data= urllib.parse.urlencode(data),headers=HEADERS)
    response = urllib.request.urlopen(request).read()
    parse = json.loads(response)
#     response = requests.post(url,HEADERS,FORM)
#     json = response.json()
    return parse

