#!/usr/bin/env python3
"""
暗号化ファイルダウンロードツール

Celestial API から最新アップロードを暗号化ダウンロードし、復号化・展開する。

使い方:
    export CELESTIAL_ENCRYPTION_KEY="暗号化キー"
    export CELESTIAL_API_URL="https://minipcserver.tailb38d9c.ts.net"
    python examples/download_encrypted_files.py --out ./downloaded

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


def decrypt_archive(encrypted_base64: str, key_hex: str) -> bytes:
    """base64 暗号文を復号化して tar.gz バイナリを返す"""
    key = bytes.fromhex(key_hex)
    raw = base64.b64decode(encrypted_base64)
    nonce = raw[:NONCE_SIZE]
    ciphertext = raw[NONCE_SIZE:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def fetch_latest(api_url: str) -> dict:
    """最新アップロードをAPIから取得する"""
    import requests

    url = f"{api_url.rstrip('/')}/api/files/secure/download/latest/"
    response = requests.get(url, timeout=300)
    response.raise_for_status()
    return response.json()


def extract_tar_gz(tar_gz_bytes: bytes, dest: str) -> list[str]:
    """tar.gz を展開してファイル一覧を返す"""
    extracted = []
    with tarfile.open(fileobj=io.BytesIO(tar_gz_bytes), mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                tar.extract(member, path=dest)
                extracted.append(member.name)
    return extracted


def main() -> None:
    parser = argparse.ArgumentParser(description="暗号化ファイルダウンロードツール")
    parser.add_argument("--out", type=str, required=True, help="展開先ディレクトリパス")
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

    # API から最新アップロードを取得
    print("最新アップロードを取得中...")
    data = fetch_latest(api_url)
    print(f"  送信者: {data['sender']}")
    print(f"  パス: {data['path']}")
    print(f"  ファイル数: {len(data['files'])}")

    # 復号化
    print("復号化中...")
    tar_gz_bytes = decrypt_archive(data["encrypted_archive"], key_hex)
    print(f"  復号化済みサイズ: {len(tar_gz_bytes) / 1024 / 1024:.2f} MB")

    # 展開
    os.makedirs(args.out, exist_ok=True)
    print(f"展開中: {args.out}")
    extracted = extract_tar_gz(tar_gz_bytes, args.out)
    print("完了!")
    for f in sorted(extracted):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
