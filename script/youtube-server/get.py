import os
import time
import requests
import youtube_dl
import glob
import csv
from argparse import ArgumentParser


def main():
    with open(os.getcwd() + '/videos/videos/list.csv') as f:
        row_channels = csv.DictReader(f)
        channels = [row for row in row_channels]
        for channel in channels:
            print(channel)
            movies = get_movies(channel)
            for movie in movies:
                print(movie)
                download(movie['id'])


def get_movies(channel):
    infos = []
    result = None
    path_url = 'https://www.googleapis.com/youtube/v3/search?key=%s&channelId=%s&part=snippet,id&order=date&maxResults=1' % (API_KEY, channel['id'])
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
        time.sleep(3)
    return infos


def download(video_id):
    print("Downloading {url} start..".format(url=video_id))
    
    OPTS = {
        'format': 'best[height=720]',
        "outtmpl": os.getcwd() + "/videos/videos/{url}.%(ext)s".format(url=video_id)
    }
    with youtube_dl.YoutubeDL(OPTS) as y:
        y.extract_info(video_id, download=True)
        print("Downloading {url} finish!".format(url=video_id))



if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-n', '--name', type=str,
                        help='show verbose message', required=False)

    args = parser.parse_args()
    name = args.name

    API_KEY = 'AIzaSyCp2x7rSOrP3ni4rHvyMXk6OSSozXJ8ogI'


    main()
