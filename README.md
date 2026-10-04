# Ribbon×Ribbon

アイドル・アニメなどの「推し活グッズ」を、ファン同士で**交換・売買**するための Web アプリです。
手放したいグッズを出品し、欲しいグッズとの交換または買取りを希望できます。

![デモ用グッズ画像](ribbonribbon/demo_images/01_penlight.png)

## 制作について

ハッカソンで制作した**チーム開発作品**です。
私（[@fujita-miyako](https://github.com/fujita-miyako)）は、チームの中で**実装の大部分**を担当しました。

※ このリポジトリはポートフォリオ公開用に、開発時のリポジトリから履歴を整理して作成しています。

## 主な機能

- ログイン / ログアウト
- グッズの出品（画像・個数・状態・説明・梱包方法・取引方法・希望グッズ・価格）
- 出品一覧・詳細表示
- キーワード検索（グッズ名・説明文）

## 使用技術

| 分類 | 技術 |
|---|---|
| 言語 | Python, HTML, CSS |
| フレームワーク | Django |
| データベース | SQLite |
| ライブラリ | Pillow（画像アップロード・デモ画像生成） |
| バージョン管理 | Git / GitHub |

## 起動手順

### 1. クローンと仮想環境の作成

```bash
git clone https://github.com/fujita-miyako/ribbon-ribbon.git
cd ribbon-ribbon
python -m venv .venv
```

仮想環境を有効化します。

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

### 2. ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. 秘密鍵（SECRET_KEY）の設定

秘密鍵はリポジトリに含めていません。環境変数 `DJANGO_SECRET_KEY` に設定してください。

```bash
# 鍵を生成
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# Windows (PowerShell)
$env:DJANGO_SECRET_KEY = "生成した鍵"
# macOS / Linux
export DJANGO_SECRET_KEY="生成した鍵"
```

### 4. データベースの作成とサーバー起動

```bash
cd ribbonribbon
python manage.py migrate
python manage.py createsuperuser   # ログイン用のユーザーを作成
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/login/ を開き、作成したユーザーでログインします。
メニュー画面は http://127.0.0.1:8000/menu/ です。

## デモデータの入れ方

架空のアイドルグループ・グッズの出品データ（10件・画像付き）を投入できます。
グループ名・キャラクター名はすべて架空のものです。

```bash
cd ribbonribbon
python manage.py seed_demo
```

- **既存の出品データはすべて削除されます**（実行前に確認が表示されます）。確認なしで実行する場合は `--noinput` を付けてください。
- 画像は `ribbonribbon/demo_images/` の PNG を使用します。画像を作り直す場合は次を実行します。

```bash
python demo_images/generate_demo_images.py
```
