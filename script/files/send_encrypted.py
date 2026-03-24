#!/usr/bin/env python3
"""
暗号化メッセージ送信サンプル

AES-256-GCM でメッセージを暗号化し、Celestial API に送信する。

使い方:
    # 鍵を生成(初回のみ。サーバーの MESSAGE_ENCRYPTION_KEY にも同じ値を設定)
    python examples/send_encrypted.py --generate-key

    # メッセージを送信
    export CELESTIAL_ENCRYPTION_KEY="生成された鍵"
    export CELESTIAL_API_URL="https://minipcserver.tailb38d9c.ts.net"
    python examples/send_encrypted.py --sender "太郎" --message "こんにちは!"

依存関係:
    pip install cryptography requests
"""

from __future__ import annotations

import argparse
import base64
import os
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# AES-GCM nonce サイズ
NONCE_SIZE = 12


def generate_key() -> str:
    """AES-256 用の鍵を生成し、16進数文字列で返す"""
    return os.urandom(32).hex()


def encrypt_message(plaintext: str, key_hex: str) -> str:
    """AES-256-GCM でメッセージを暗号化する

    Returns:
        base64(nonce + ciphertext + tag)
    """
    key = bytes.fromhex(key_hex)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def send_message(api_url: str, encrypted_content: str, sender: str) -> dict:
    """暗号化メッセージを API に送信する"""
    import requests

    url = f"{api_url.rstrip('/')}/api/messages/secure/"
    response = requests.post(
        url,
        json={
            "encrypted_content": encrypted_content,
            "sender": sender,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="暗号化メッセージ送信ツール")
    parser.add_argument("--generate-key", action="store_true", help="新しい暗号化キーを生成")
    parser.add_argument("--sender", type=str, help="送信者名")
    parser.add_argument("--message", type=str, help="送信するメッセージ")
    parser.add_argument("--api-url", type=str, help="API URL (環境変数 CELESTIAL_API_URL でも可)")
    parser.add_argument("--key", type=str, help="暗号化キー (環境変数 CELESTIAL_ENCRYPTION_KEY でも可)")
    args = parser.parse_args()

    # 鍵生成モード
    if args.generate_key:
        key = generate_key()
        print(f"生成された暗号化キー:\n{key}")
        print("\nサーバー側: MESSAGE_ENCRYPTION_KEY 環境変数に設定してください")
        print("クライアント側: CELESTIAL_ENCRYPTION_KEY 環境変数に設定してください")
        return

    # メッセージ送信モード
    key_hex = args.key or os.environ.get("CELESTIAL_ENCRYPTION_KEY", "")
    if not key_hex:
        print("エラー: 暗号化キーが必要です (--key または CELESTIAL_ENCRYPTION_KEY)", file=sys.stderr)
        sys.exit(1)

    api_url = args.api_url or os.environ.get("CELESTIAL_API_URL", "")
    if not api_url:
        print("エラー: API URL が必要です (--api-url または CELESTIAL_API_URL)", file=sys.stderr)
        sys.exit(1)

    sender = args.sender
    message = args.message

    if not sender or not message:
        print("エラー: --sender と --message は必須です", file=sys.stderr)
        sys.exit(1)

    # 暗号化して送信
    encrypted = encrypt_message(message, key_hex)
    print(f"暗号化済み: {encrypted[:40]}...")

    result = send_message(api_url, encrypted, sender)
    print(f"送信成功! ID: {result['id']}")
    print(f"  送信者: {result['sender']}")
    print(f"  内容: {result['content']}")
    print(f"  日時: {result['created_at']}")


if __name__ == "__main__":
    main()
