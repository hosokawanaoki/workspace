#!/usr/bin/env python3
"""
YouTube Downloader - 統合版
動画、音声（MP3）、プレイリストのダウンロードに対応
"""

import os
import sys
import yt_dlp
from argparse import ArgumentParser


def download_audio(url, output_path='./downloads', quality='192'):
    """
    YouTube動画を音声（MP3）形式でダウンロード

    Args:
        url: YouTube URL
        output_path: 出力先ディレクトリ
        quality: 音質（kbps）
    """
    # URLのクエリパラメータを削除
    url = url.split('&pp')[0] if '&pp' in url else url

    print(f"[音声ダウンロード] {url}")

    opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': os.path.join(output_path, '%(title)s_%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    print(f"[完了] 音声ダウンロード完了")


def download_video(url, output_path='./downloads', quality='best'):
    """
    YouTube動画をダウンロード

    Args:
        url: YouTube URL
        output_path: 出力先ディレクトリ
        quality: 動画品質（best, 1080p, 720p, 480pなど）
    """
    # URLのクエリパラメータを削除
    url = url.split('&pp')[0] if '&pp' in url else url

    print(f"[動画ダウンロード] {url}")

    # 品質設定のマッピング
    quality_formats = {
        'best': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'worst': 'worstvideo+bestaudio/worst',
    }

    format_str = quality_formats.get(quality, quality)

    opts = {
        'format': format_str,
        'outtmpl': os.path.join(output_path, '%(title)s_%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    print(f"[完了] 動画ダウンロード完了")


def download_playlist(url, output_path='./downloads', mode='video', quality='best'):
    """
    プレイリストをダウンロード

    Args:
        url: プレイリストURL
        output_path: 出力先ディレクトリ
        mode: 'video' または 'audio'
        quality: 品質設定
    """
    # URLのクエリパラメータを削除
    url = url.split('&pp')[0] if '&pp' in url else url

    print(f"[プレイリストダウンロード] {url}")
    print(f"[モード] {mode}")

    if mode == 'audio':
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality if quality.isdigit() else '192',
            }],
            'outtmpl': os.path.join(output_path, '%(playlist)s/%(title)s_%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,  # エラーがあっても続行
        }
    else:  # video
        quality_formats = {
            'best': 'bestvideo+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'worst': 'worstvideo+bestaudio/worst',
        }
        format_str = quality_formats.get(quality, quality)

        opts = {
            'format': format_str,
            'outtmpl': os.path.join(output_path, '%(playlist)s/%(title)s_%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,  # エラーがあっても続行
        }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    print(f"[完了] プレイリストダウンロード完了")


def interactive_mode():
    """
    対話型モード（従来の動作）
    """
    print("=== YouTube Downloader（対話型モード）===")
    print("URLを入力してください（終了: Ctrl+C）")

    output_path = './downloads'
    os.makedirs(output_path, exist_ok=True)

    while True:
        try:
            url = input("\nURL: ").strip()
            if not url:
                continue

            # デフォルトで音声ダウンロード（従来の動作）
            download_audio(url, output_path)

        except KeyboardInterrupt:
            print("\n終了します")
            break
        except Exception as e:
            print(f"エラー: {e}")
            continue


def main():
    parser = ArgumentParser(
        description='YouTube動画・音声ダウンローダー',
        epilog='例: python youtube-dl.py -m audio -u "https://youtube.com/watch?v=..."'
    )

    parser.add_argument(
        '-m', '--mode',
        choices=['video', 'audio', 'playlist'],
        help='ダウンロードモード: video（動画）, audio（音声/MP3）, playlist（プレイリスト）'
    )

    parser.add_argument(
        '-u', '--url',
        help='YouTube URL（動画、プレイリスト）'
    )

    parser.add_argument(
        '-o', '--output',
        default='./downloads',
        help='出力先ディレクトリ（デフォルト: ./downloads）'
    )

    parser.add_argument(
        '-q', '--quality',
        default='best',
        help='品質設定（動画: best/1080p/720p/480p、音声: kbps値、デフォルト: best/192）'
    )

    args = parser.parse_args()

    # 引数なしの場合は対話型モード
    if not args.mode and not args.url:
        interactive_mode()
        return

    # モードまたはURLが指定されている場合は必須チェック
    if not args.mode or not args.url:
        parser.error('--mode と --url の両方を指定してください（または引数なしで対話型モード）')

    # 出力ディレクトリを作成
    os.makedirs(args.output, exist_ok=True)

    try:
        if args.mode == 'audio':
            download_audio(args.url, args.output, args.quality)
        elif args.mode == 'video':
            download_video(args.url, args.output, args.quality)
        elif args.mode == 'playlist':
            # プレイリストのサブモードを選択
            print("プレイリストのダウンロード形式を選択してください:")
            print("1. 動画")
            print("2. 音声（MP3）")
            choice = input("選択 (1/2): ").strip()

            playlist_mode = 'video' if choice == '1' else 'audio'
            download_playlist(args.url, args.output, playlist_mode, args.quality)

    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()