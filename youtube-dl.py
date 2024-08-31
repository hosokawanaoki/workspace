import os
import time
import requests
import yt_dlp
import glob
import csv
import datetime
from argparse import ArgumentParser
import glob


def download():
    

    while True: 
        print("prease input=")
        txt = input()
        url = txt.split('&pp')[0]
        print(url)
        print("Downloading {url} start..".format(url=url))
        opts = {
            'format': 'worstvideo+bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            "outtmpl": out_path + "/%(title)s_%(id)s.%(ext)s"
        }
        with yt_dlp.YoutubeDL(opts) as y:
            y.extract_info(url, download=True)
            print("Downloading {url} finish!".format(url=url))

if __name__ == '__main__':

    parser = ArgumentParser()

    out_path = './opt'
    download()