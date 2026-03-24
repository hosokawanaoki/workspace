#!/usr/bin/env python3
"""
暗号化ファイル転送ツール

ディレクトリを tar.gz にまとめ、AES-256-GCM で暗号化して Celestial API に送信する。

使い方:
    # ディレクトリを送信
    export CELESTIAL_ENCRYPTION_KEY="暗号化キー"
    export CELESTIAL_API_URL="https://minipcserver.tailb38d9c.ts.net"
    python examples/send_encrypted_files.py --dir ./my_files --sender "太郎"

    # 鍵生成は send_encrypted.py を参照
    python examples/send_encrypted.py --generate-key

依存関係:
    pip install cryptography requests
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import sys
import tarfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024  # 100MB


def create_tar_gz(directory: str) -> bytes:
    """ディレクトリを tar.gz にまとめてバイナリを返す"""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(directory, arcname=".")
    return buf.getvalue()


def encrypt_archive(tar_gz_bytes: bytes, key_hex: str) -> str:
    """tar.gz を AES-256-GCM で暗号化し、base64 文字列を返す"""
    key = bytes.fromhex(key_hex)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, tar_gz_bytes, None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def send_archive(api_url: str, encrypted_archive: str, sender: str) -> dict:
    """暗号化アーカイブを API に送信する"""
    import requests

    url = f"{api_url.rstrip('/')}/api/files/secure/upload/"
    response = requests.post(
        url,
        json={
            "encrypted_archive": encrypted_archive,
            "sender": sender,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="暗号化ファイル転送ツール")
    parser.add_argument("--dir", type=str, required=True, help="送信するディレクトリパス")
    parser.add_argument("--sender", type=str, required=True, help="送信者名")
    parser.add_argument("--api-url", type=str, help="API URL (環境変数 CELESTIAL_API_URL でも可)")
    parser.add_argument("--key", type=str, help="暗号化キー (環境変数 CELESTIAL_ENCRYPTION_KEY でも可)")
    args = parser.parse_args()

    key_hex = args.key or os.environ.get("CELESTIAL_ENCRYPTION_KEY", "")
    if not key_hex:
        print("エラー: 暗号化キーが必要です (--key または CELESTIAL_ENCRYPTION_KEY)", file=sys.stderr)
        sys.exit(1)

    api_url = args.api_url or os.environ.get("CELESTIAL_API_URL", "")
    if not api_url:
        print("エラー: API URL が必要です (--api-url または CELESTIAL_API_URL)", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.dir):
        print(f"エラー: ディレクトリが見つかりません: {args.dir}", file=sys.stderr)
        sys.exit(1)

    # tar.gz 作成
    print(f"アーカイブ作成中: {args.dir}")
    tar_gz_bytes = create_tar_gz(args.dir)
    size_mb = len(tar_gz_bytes) / 1024 / 1024
    print(f"  サイズ: {size_mb:.2f} MB")

    if len(tar_gz_bytes) > MAX_ARCHIVE_SIZE:
        print("エラー: アーカイブサイズが上限 (100MB) を超えています", file=sys.stderr)
        sys.exit(1)

    # 暗号化
    print("暗号化中...")
    encrypted = encrypt_archive(tar_gz_bytes, key_hex)
    print(f"  暗号化済みサイズ: {len(encrypted) / 1024 / 1024:.2f} MB (base64)")

    # 送信
    print(f"送信中: {api_url}")
    result = send_archive(api_url, encrypted, args.sender)
    print("送信成功!")
    print(f"  保存先: {result['path']}")
    print(f"  送信者: {result['sender']}")
    print(f"  ファイル数: {len(result['files'])}")
    for f in result["files"]:
        print(f"    - {f}")


if __name__ == "__main__":
    main()
