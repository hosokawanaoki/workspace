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
    file_remove()
    with open(os.path.dirname(__file__) + '/videos/list.csv') as f:
        row_channels = csv.DictReader(f)
        videos = [row for row in row_channels]
        for video in videos:
            download(video)

def file_remove():
    files = glob.glob(os.path.dirname(__file__) + '/videos/videos/*.mp3')
    for file_path in files:
        try:
            os.remove(file_path)
        except ValueError:
            raise ValueError("Incorrect data format, should be %Y-%m-%dT%H:%M:%SZ")

def download(video):
    print("Downloading {url} start..".format(url=video['id']))
    opts = {
        'format': 'worstvideo+bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        "outtmpl": os.path.dirname(__file__)  + "/videos/videos/%(title)s.%(ext)s"
    }
    with youtube_dl.YoutubeDL(opts) as y:
        y.extract_info(video['id'], download=True)
        print("Downloading {url} finish!".format(url=video['id']))

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-n', '--name', type=str,
                        help='show verbose message', required=False)

    args = parser.parse_args()
    name = args.name

    # BASE_PATH = 'https://www.googleapis.com/youtube/v3/search'
    # API_KEY = 'AIzaSyCp2x7rSOrP3ni4rHvyMXk6OSSozXJ8ogI'
    main()
