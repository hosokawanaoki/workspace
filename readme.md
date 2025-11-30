# 個人用便利ツール集

個人で使用している便利ツールやスクリプトをまとめたリポジトリです。
主にRaspberry Piの自動セットアップ、YouTube動画のダウンロード、ファイル共有などの自動化ツールを含んでいます。

## 目次

- [ディレクトリ構成](#ディレクトリ構成)
- [インフラ設定](#インフラ設定)
- [スクリプト](#スクリプト)
  - [YouTube-dl（統合版）](#youtube-dl統合版)
  - [Raspberry Pi自動化](#raspberry-pi自動化)
- [前提条件](#前提条件)
- [uv + taskipyによる開発環境](#uv--taskipyによる開発環境)

## ディレクトリ構成

```text
.
├── infra/                      # インフラ関連スクリプト
├── script/                     # 各種スクリプト
│   ├── youtube-dl.py           # YouTube動画・音声・プレイリストダウンローダー（統合版）
│   ├── raspi/                  # Raspberry Pi用Ansibleプレイブック
│   │   ├── init.yml            # 初期設定（ロケール・タイムゾーン・固定IP）
│   │   ├── nfs.yml             # NFSサーバー構築
│   │   ├── samba.yml           # Sambaファイル共有設定
│   │   └── raspi-host          # Ansibleホスト定義ファイル
│   └── youtube-server/         # YouTubeダウンロードサーバー
│       ├── youtube-server.yml  # サーバーセットアップ用Ansible
│       ├── get.py              # YouTube動画取得スクリプト
│       └── get_by_playlist.py  # プレイリスト対応版
├── youtube-dl.py               # YouTube DL（統合版・メイン）
├── pyproject.toml              # uvプロジェクト設定（依存管理 + taskipy）
└── readme.md                   # このファイル
```

---

## インフラ設定

### Ansibleのセットアップ

このプロジェクトではAnsibleを**uv**経由で管理しています。

**インストール方法**:

```bash
# 1. uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Ansibleを含む依存パッケージのインストール
uv sync --extra infra

# 3. sshpassのインストール（パスワード認証を使う場合）
# Ubuntu/Debian:
sudo apt-get install sshpass
```

**Ansible実行方法**:

```bash
# uvで管理されたAnsibleを使用
uv run ansible-playbook -i script/raspi/raspi-host -u pi --ask-pass script/raspi/init.yml
```

---

## スクリプト

### YouTube-dl（統合版）

**ファイル**: [youtube-dl.py](youtube-dl.py)

YouTube動画・音声・プレイリストをダウンロードできる統合スクリプトです。

**機能**:

- 動画ダウンロード（MP4形式、品質選択可能）
- 音声ダウンロード（MP3形式、音質選択可能）
- プレイリスト一括ダウンロード（動画/音声選択可能）
- 対話型モード（従来の動作）
- コマンドライン引数による柔軟な操作

**セットアップ（uv推奨）**:

```bash
# 1. uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 依存パッケージのインストール
uv sync

# 3. システムパッケージ（ffmpeg）のインストール
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
```

**使い方（taskipyコマンド）**:

```bash
# 対話型モード（URLを入力してMP3ダウンロード）
uv run task download

# 音声（MP3）ダウンロード
uv run task audio "https://youtube.com/watch?v=..."

# 動画ダウンロード（デフォルト品質）
uv run task video "https://youtube.com/watch?v=..."

# 動画ダウンロード（720p）
uv run task video-720p "https://youtube.com/watch?v=..."

# 動画ダウンロード（1080p）
uv run task video-1080p "https://youtube.com/watch?v=..."

# プレイリストダウンロード
uv run task playlist "https://youtube.com/playlist?list=..."

# ヘルプ表示
uv run task help
```

**使い方（直接実行）**:

```bash
# 対話型モード
uv run python youtube-dl.py

# 音声ダウンロード
uv run python youtube-dl.py -m audio -u "YouTubeのURL"

# 動画ダウンロード
uv run python youtube-dl.py -m video -u "YouTubeのURL" -q 1080p

# プレイリストダウンロード
uv run python youtube-dl.py -m playlist -u "プレイリストのURL"

# 出力先指定
uv run python youtube-dl.py -m audio -u "URL" -o ./my_downloads
```

**オプション**:

- `-m`, `--mode`: ダウンロードモード（video/audio/playlist）
- `-u`, `--url`: YouTube URL
- `-o`, `--output`: 出力先ディレクトリ（デフォルト: ./downloads）
- `-q`, `--quality`: 品質設定
  - 動画: best, 1080p, 720p, 480p（デフォルト: best）
  - 音声: kbps値（デフォルト: 192）

---

### Raspberry Pi自動化

Raspberry Piの各種セットアップを自動化するAnsibleプレイブック集です。

#### 1. 初期設定

**ファイル**: [script/raspi/init.yml](script/raspi/init.yml)

Raspberry Piの基本設定を自動化します。

**設定内容**:

- ロケール: `ja_JP.UTF-8`
- タイムゾーン: `Asia/Tokyo`
- キーボードレイアウト: `jp`
- 無線LAN固定IP設定（`192.168.0.22/24`）
- vimのインストール

**実行方法**:

```bash
uv run ansible-playbook -i script/raspi/raspi-host -u pi --ask-pass script/raspi/init.yml
```

**注意**: 実行後は手動でrebootが必要です（IPアドレスが変更されるため）

---

#### 2. NFSサーバー構築

**ファイル**: [script/raspi/nfs.yml](script/raspi/nfs.yml)

NFSサーバーを構築してファイル共有を設定します。

**設定内容**:

- nfs-kernel-serverのインストール
- `/srv/nfs` をNFS共有ディレクトリとして設定
- `192.168.3.0/24` ネットワークに共有を許可
- rpcbind・nfs-serverサービスの自動起動設定

**実行方法**:

```bash
uv run ansible-playbook -i script/raspi/raspi-host -u pi --ask-pass script/raspi/nfs.yml
```

---

#### 3. Sambaファイル共有

**ファイル**: [script/raspi/samba.yml](script/raspi/samba.yml)

Windowsからもアクセスできるファイル共有をSambaで構築します。

**設定内容**:

- Sambaのインストール
- `/samba/share` を共有ディレクトリとして設定
- `/media/pi/Elements/コンテンツ` も共有（外付けHDD想定）
- パーミッション: 0777（読み書き可能）

**実行方法**:

```bash
uv run ansible-playbook -i script/raspi/raspi-host -u pi --ask-pass script/raspi/samba.yml
```

**注意**: 実行後は自動的にrebootされます

---

## 前提条件

### 共通

- **Python 3.x**
- **pip3**

### Ansible関連

- **Ansible** 2.9以上推奨
- **sshpass** （パスワード認証を使う場合）

### Raspberry Pi

- **Raspberry Pi OS**（旧Raspbian）
- デフォルトユーザー: `pi`
- SSH有効化済み

### インストール例

**uv経由でのセットアップ（推奨）**:

```bash
# 1. uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. プロジェクトの依存関係をインストール
uv sync

# 3. Ansible関連もインストールする場合
uv sync --extra infra

# 4. システムパッケージ（sshpass）のインストール
# Ubuntu/Debian:
sudo apt-get install sshpass
```

---

## uv + taskipyによる開発環境

このリポジトリでは、Python依存管理に**uv**、タスクランナーに**taskipy**を使用しています。

### uvとは

[uv](https://github.com/astral-sh/uv)は、高速なPythonパッケージマネージャーです。pipやpip-toolsの代替として使用でき、依存関係の解決とインストールが非常に高速です。

### セットアップ

```bash
# uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存パッケージのインストール
uv sync
```

### taskipyコマンド一覧

[pyproject.toml](pyproject.toml)で定義されているタスク:

```bash
# YouTube-dl関連
uv run task download         # 対話型モード（URLを入力してMP3ダウンロード）
uv run task dl               # downloadのエイリアス
uv run task audio "URL"      # 音声（MP3）ダウンロード
uv run task mp3 "URL"        # audioのエイリアス
uv run task video "URL"      # 動画ダウンロード（best品質）
uv run task video-720p "URL" # 動画ダウンロード（720p）
uv run task video-1080p "URL" # 動画ダウンロード（1080p）
uv run task playlist "URL"   # プレイリストダウンロード

# ユーティリティ
uv run task setup            # 依存パッケージのインストール（uv sync）
uv run task install          # setupのエイリアス
uv run task help             # youtube-dl.pyのヘルプ表示
```

### カスタマイズ

タスクを追加・変更したい場合は、[pyproject.toml](pyproject.toml)の`[tool.taskipy.tasks]`セクションを編集してください。

```toml
[tool.taskipy.tasks]
my-task = "python my-script.py"
```

---

## Ansibleの基本的な使い方

Raspberry Piに対してAnsibleプレイブックを実行する基本コマンド:

```bash
# uv経由でAnsibleを実行（推奨）
uv run ansible-playbook <プレイブック.yml> \
  -i script/raspi/raspi-host \
  -u pi \
  --ask-pass \
  -e 'ansible_python_interpreter=/usr/bin/python3'
```

**オプション説明**:

- `-i script/raspi/raspi-host`: ホストファイルを指定
- `-u pi`: 接続ユーザー名
- `--ask-pass`: SSH接続時にパスワードを入力
- `-e 'ansible_python_interpreter=/usr/bin/python3'`: Python3を使用

---

## ライセンス

個人用のため特にライセンスは設定していません。ご自由にお使いください。
