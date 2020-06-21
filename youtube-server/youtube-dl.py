#!/usr/bin/env python
# coding: utf-8

import os
import glob
import youtube_dl
from argparse import ArgumentParser
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# consts
VIDEO_DIR = os.path.join("/youtube", "videos")
OPTS = {
    "outtmpl": "{VIDEO_DIR}/%(title)s.mp4".format(VIDEO_DIR=VIDEO_DIR)
}


def download(url):
    """
    Download video from YouTube.

    Parameters
    ----------
    url : str
        YouTube video URL

    Returns
    ----------
    info : dict
        Downloaded video info.
    """
    print("Downloading {url} start..".format(url=url))
    with youtube_dl.YoutubeDL(OPTS) as y:
        info = y.extract_info(url, download=True)
        print("Downloading {url} finish!".format(url=url))
    return info


def rename(info):
    """
    Rename downloaded video filename as camelcase.

    Parameters
    ----------
    info : dict
        Downloaded video info.
    """
    title = info["title"]
    pattern = '{VIDEO_DIR}/{title}.mp4'.format(
        VIDEO_DIR=VIDEO_DIR, title=title)
    for v in glob.glob(pattern, recursive=True):
        print("{title}.mp4 found! Renaming start..".format(title=title))
        file_path = os.path.join(VIDEO_DIR, v)
        new_file_path = file_path.replace(' ', '_')
        os.rename(file_path, new_file_path)
        print("Renaming finish!".format(title))


def drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1 = drive.CreateFile({'title': 'Hello.txt'})
    # Set content of the file from given string.
    file1.SetContentString('Hello World!')
    file1.Upload()


if __name__ == "__main__":
    parser = ArgumentParser(description='youtubepath')
    parser.add_argument('-u', '--url', type=str, help='url', required=True)
    args = parser.parse_args()
    url = args.url
    info = download(url)
    rename(info)
    drive()
