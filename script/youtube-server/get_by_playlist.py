import os
import time
import requests
import youtube_dl
import glob
import csv
import datetime
from argparse import ArgumentParser
import glob

def main():
    download()

def file_remove():
    files = glob.glob(os.getcwd() + '/videos/videos/*.mp4')
    for file_path in files:
        try:
            file_timestamp_str = os.path.basename(file_path).split("|", 1)[0]
            file_timestamp_date = datetime.datetime.strptime(file_timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
            if file_timestamp_date < (datetime.datetime.now() - datetime.timedelta(1)):
                os.remove(file_path)
        except ValueError:
            raise ValueError("Incorrect data format, should be %Y-%m-%dT%H:%M:%SZ")
            

def get_movies(channel):
    infos = []
    result = None
    path_url = '%s?key=%s&channelId=%s&part=snippet,id&order=date&maxResults=1' \
        % (BASE_PATH, API_KEY, channel['id'])
    tmp_url = ''
    while True:
        response = requests.get(path_url + tmp_url)
        if response.status_code != 200:
            print('error :'+ path_url + tmp_url )
            response.raise_for_status()
            break
        result = response.json()
        infos.extend(
            [
                {
                    'id':item['id']['videoId'],
                    'title':item['snippet']['title'],
                    'desc':item['snippet']['description'],
                    'at':item['snippet']['publishedAt']
                }
                for item in result['items'] if item['id']['kind'] == 'youtube#video'
            ]
        )
        if 'nextPageToken' not in result.keys():
            tmp_url = "&pageToken={result['nextPageToken']}"
        else:
            tmp_url = ''
            print('正常終了')
            break
        time.sleep(20)
    return infos


def download():
    opts = {
        'playlist-items': 'best[height<=720]',
        "outtmpl": os.getcwd() + "/videos/videos/%(id)s.%(ext)s".format(url="title")
    }
    with youtube_dl.YoutubeDL(opts) as y:
        y.extract_info("PLx7dbRz_yGZBrGd2KezFANQMv1F71UbF8", download=True) 



if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-n', '--name', type=str,
                        help='show verbose message', required=False)

    args = parser.parse_args()
    name = args.name

    BASE_PATH = 'https://www.googleapis.com/youtube/v3/search'
    API_KEY = 'AIzaSyCp2x7rSOrP3ni4rHvyMXk6OSSozXJ8ogI'
    main()
