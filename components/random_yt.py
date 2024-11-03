from googleapiclient.discovery import build
import random
from config import config as cfg
import string

DEVELOPER_KEY = cfg.GOOGLE_API_KEY
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

prefix = ['IMG ', 'IMG_', 'IMG-', 'DSC ']
postfix = [' MOV', '.MOV', ' .MOV']


def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))

    search_response = youtube.search().list(
        q=search,
        part='snippet',
        maxResults=50,
    ).execute()

    videos = []

    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append('%s' % (search_result['id']['videoId']))
    return random.choice(videos)
