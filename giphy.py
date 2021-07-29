import requests

# gif_url = "http://api.giphy.com/v1/gifs/search"
# sticker_url = "http://api.giphy.com/v1/stickers/search"
# ?q=ryan+gosling&api_key=YOUR_API_KEY&limit=5
# Currently we are limited to 42 requests per hour and 1000 per day
# Can upgrade hopefully with student plead once we have a beta version working


def get_input(option):
    if option == 'gif':
        print('Searching for gif')
        keyword = input('Enter search query ')
        return keyword
    elif option == 'sticker':
        print('Searching for sticker')
        keyword = input('Enter search query ')
        return keyword


def build_url(option, keyword):
    API_KEY = "ZAB9b4mJoA3j00QSW2GSkIlJ43hdoXjJ"
    keyword = keyword.replace(' ', '+')
    keyword = keyword.lower()
    URL = (
        f'http://api.giphy.com/v1/{option}/search?q={keyword}&'
        f'api_key={API_KEY}&limit=1'
    )
    return URL


def get_results(url):
    response = requests.get(url)
    data = response.json()
    return data


def parse_json(data):
    try:
        result = data['data'][0]['embed_url']
        return result
    except BaseException:
        result = None
        return result


def print_test():
    keyword = get_input('gif')
    gif_url = build_url('gifs', keyword)
    json = get_results(gif_url)
    gif = parse_json(json)
    print(gif)
    keyword = get_input('sticker')
    sticker_url = build_url('stickers', keyword)
    json = get_results(sticker_url)
    sticker = parse_json(json)
    print(sticker)


print_test()
