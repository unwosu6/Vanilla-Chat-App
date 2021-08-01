import requests


def get_input():
    channel = input("Enter search query keyword: ")
    return channel


def get_search_results(api_key, keyword):
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet" + \
        "&maxResults=1&q=" + \
        keyword + "&key=" + api_key

    response = requests.get(url)
    data = response.json()
    return data


def extract_info_json(data):
    if data != "":
        video_id = data['items'][0]['id']['videoId']
        return video_id
    else:
        return []


def video_url(video_id):
    if video_id != "":
        return "https://www.youtube.com/embed/" + video_id
    else:
        return ""

# This function is for testing outside of deployment


def print_result():
    api_key = "AIzaSyBGkGFRJ1Lzdsizug87FXPAl-yLuOjucdU"
    api_key2 = "AIzaSyAG-YgDxNNokUoSl8R3wPrakujPLXOE2fw"
    keyword = get_input()
    results = get_search_results(api_key2, keyword)
    video_id = extract_info_json(results)
    url = video_url(video_id)
    # print(results)
    print(url)


# Remove this testing function later when implemented into main.py
# print_result()
