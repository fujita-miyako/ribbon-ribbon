"""デモ動画撮影用に、出品データを架空のダミーデータへ差し替える管理コマンド。

    python manage.py seed_demo            # 確認してから実行
    python manage.py seed_demo --noinput  # 確認なしで実行

画像は demo_images/ の PNG（generate_demo_images.py で生成）を使う。
グループ名・メンバー名はすべて架空のもの。
"""
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from menu.models import Page

DEMO_IMAGE_DIR = Path(settings.BASE_DIR) / "demo_images"
UPLOAD_PREFIX = "demo_"  # seed_demo で保存した画像の目印（再実行時に掃除する）

# 架空グループ
#   Lumière Ribbon（ルミリボ）     : 桜庭ひより / 月城まりん / 星野ことは
#   STELLAR CANDY（ステキャン）    : ノア / ユズ / レイ
#   Honey Moon Parade（ハニパレ）  : 白雪ゆめ / 雛森あんず
DEMO_PAGES = [
    {
        "image": "01_penlight.png",
        "name": "ルミリボ 公式ペンライト ver.2（スターライト）",
        "quantity": 1,
        "condition": "like_new",
        "description": "Lumière Ribbon 2nd ライブ「sweet starlight」で購入した公式ペンライトです。"
                       "ライブで1回のみ使用、点灯確認済みです。15色切り替え・電池は抜いて保管していました。"
                       "外箱と取扱説明書もお付けします。",
        "packaging_method": "外箱ごとプチプチで包み、宅配便の60サイズ箱でお送りします。",
        "trade_preference": "purchase",
        "wanted_item_name": "特になし（買取り希望）",
        "wanted_item_details": "お値下げは500円までご相談ください。",
        "price": 2800,
        "days_ago": 0, "hours_ago": 3,
    },
    {
        "image": "02_acrylic_keychain.png",
        "name": "ステキャン ノア ハートアクリルキーホルダー",
        "quantity": 1,
        "condition": "new",
        "description": "STELLAR CANDY ポップアップストア限定のランダムアクキー（ノア）です。"
                       "開封のみで保護フィルムも付いたままです。",
        "packaging_method": "OPP袋に入れ、硬質ケースで挟んで封筒でお送りします。",
        "trade_preference": "exchange",
        "wanted_item_name": "ステキャン ユズ ハートアクリルキーホルダー",
        "wanted_item_details": "同シリーズのユズを探しています。未開封・開封済みどちらでも大丈夫です。"
                               "郵送での同時発送を希望します。",
        "price": 900,
        "days_ago": 0, "hours_ago": 9,
    },
    {
        "image": "03_trading_card.png",
        "name": "ルミリボ 桜庭ひより トレカ SP No.07",
        "quantity": 1,
        "condition": "new",
        "description": "1stアルバム封入のスペシャルトレカ（ホロ仕様）、桜庭ひよりのNo.07です。"
                       "開封後すぐにスリーブ・硬質ケースに入れて保管していました。目立つ傷はありません。",
        "packaging_method": "スリーブ＋硬質ケースに入れ、防水のため OPP 袋で包んで封筒でお送りします。",
        "trade_preference": "exchange",
        "wanted_item_name": "ルミリボ 月城まりん トレカ SP",
        "wanted_item_details": "まりんのSPトレカであれば番号は問いません。"
                               "トレカ2枚との交換もご相談ください。",
        "price": 1500,
        "days_ago": 1, "hours_ago": 2,
    },
    {
        "image": "04_can_badge.png",
        "name": "ハニパレ 缶バッジ 3種セット",
        "quantity": 3,
        "condition": "like_new",
        "description": "Honey Moon Parade の ツアーグッズ缶バッジ（56mm）3種セットです。"
                       "リボン柄・ハート柄・スター柄が1つずつ入っています。痛バッグには付けていません。",
        "packaging_method": "1つずつ OPP 袋に入れ、緩衝材で包んで封筒でお送りします。",
        "trade_preference": "purchase",
        "wanted_item_name": "特になし（買取り希望）",
        "wanted_item_details": "バラ売りは行っていません。3種セットでのお取引をお願いします。",
        "price": 1200,
        "days_ago": 1, "hours_ago": 7,
    },
    {
        "image": "05_cd.png",
        "name": "ステキャン 1st Album「Sugar Galaxy」初回限定盤",
        "quantity": 1,
        "condition": "good",
        "description": "STELLAR CANDY の 1stアルバム初回限定盤です。数回再生しました。"
                       "ケースに小さな擦れがありますが、ディスクに傷はありません。"
                       "特典のトレカ・応募券は付属しません。",
        "packaging_method": "プチプチで包み、厚紙で補強した封筒でお送りします。",
        "trade_preference": "purchase",
        "wanted_item_name": "特になし（買取り希望）",
        "wanted_item_details": "即購入OKです。",
        "price": 2200,
        "days_ago": 2, "hours_ago": 4,
    },
    {
        "image": "06_acrylic_stand.png",
        "name": "ルミリボ 月城まりん スターアクスタ",
        "quantity": 1,
        "condition": "new",
        "description": "まりんの生誕祭グッズのスター型アクリルスタンドです。未開封のままお譲りします。"
                       "生産数が少ないアイテムなので、大切にしてくださる方にお譲りしたいです。",
        "packaging_method": "未開封の袋のまま緩衝材で包み、箱に入れて宅配便でお送りします。",
        "trade_preference": "exchange",
        "wanted_item_name": "ルミリボ 星野ことは スターアクスタ",
        "wanted_item_details": "ことはの生誕祭アクスタと交換していただける方を探しています。"
                               "開封済みでも、目立つ傷がなければ大丈夫です。",
        "price": 2500,
        "days_ago": 3, "hours_ago": 1,
    },
    {
        "image": "07_uchiwa.png",
        "name": "ハニパレ 白雪ゆめ ファンサうちわ",
        "quantity": 1,
        "condition": "good",
        "description": "ゆめのファンサうちわ（ジャンボサイズ）です。ライブで2回使用しました。"
                       "持ち手に少し使用感がありますが、面の印刷はきれいです。",
        "packaging_method": "大判の封筒に厚紙と一緒に入れ、折れないようにしてお送りします。",
        "trade_preference": "exchange",
        "wanted_item_name": "ハニパレ 雛森あんず ファンサうちわ",
        "wanted_item_details": "あんずのうちわであればデザインは問いません。お互いに使用感ありでOKな方を希望します。",
        "price": 1000,
        "days_ago": 4, "hours_ago": 6,
    },
    {
        "image": "08_sticker.png",
        "name": "ステキャン ステッカーセット",
        "quantity": 2,
        "condition": "new",
        "description": "STELLAR CANDY の公式ステッカーシートです。同じものが2枚あります。"
                       "星・ハート・リボンのダイカットステッカー入りで、未使用です。",
        "packaging_method": "OPP 袋に入れ、厚紙で挟んで封筒でお送りします。",
        "trade_preference": "purchase",
        "wanted_item_name": "特になし（買取り希望）",
        "wanted_item_details": "1枚のみのご購入も可能です（1枚400円）。",
        "price": 700,
        "days_ago": 5, "hours_ago": 3,
    },
    {
        "image": "09_muffler_towel.png",
        "name": "ルミリボ LIVE TOUR マフラータオル",
        "quantity": 1,
        "condition": "fair",
        "description": "Lumière Ribbon LIVE TOUR「sweet starlight」のマフラータオルです。"
                       "何度か使用・洗濯しているため、フリンジ部分にほつれが少しあります。",
        "packaging_method": "たたんで OPP 袋に入れ、ゆうパケットでお送りします。",
        "trade_preference": "purchase",
        "wanted_item_name": "特になし（買取り希望）",
        "wanted_item_details": "使用感があるため、お安めにしています。",
        "price": 800,
        "days_ago": 6, "hours_ago": 8,
    },
    {
        "image": "10_tote_bag.png",
        "name": "ハニパレ リボンロゴ トートバッグ",
        "quantity": 1,
        "condition": "like_new",
        "description": "Honey Moon Parade の ファンクラブ入会特典トートバッグです。"
                       "一度試しに持っただけで、汚れや破れはありません。A4サイズが入ります。",
        "packaging_method": "たたんで OPP 袋に入れ、ゆうパケットでお送りします。",
        "trade_preference": "exchange",
        "wanted_item_name": "ルミリボ 星野ことは 缶バッジ",
        "wanted_item_details": "ことはの缶バッジ2個以上と交換していただける方を探しています。種類は問いません。",
        "price": 1800,
        "days_ago": 8, "hours_ago": 5,
    },
]


class Command(BaseCommand):
    help = "出品データ（Page）をすべて削除し、デモ用の架空データを投入します。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput", "--no-input", action="store_false", dest="interactive",
            help="確認プロンプトを表示せずに実行します。",
        )

    def handle(self, *args, **options):
        missing = [d["image"] for d in DEMO_PAGES if not (DEMO_IMAGE_DIR / d["image"]).exists()]
        if missing:
            raise CommandError(
                f"{DEMO_IMAGE_DIR} に画像がありません: {', '.join(missing)}\n"
                "先に python demo_images/generate_demo_images.py を実行してください。"
            )

        count = Page.objects.count()
        if options["interactive"] and count:
            answer = input(f"既存の出品データ {count} 件を削除して、デモデータに差し替えます。よろしいですか？ [y/N]: ")
            if answer.strip().lower() not in ("y", "yes"):
                self.stdout.write("中止しました。")
                return

        self._remove_previous_demo_files()

        now = timezone.now()
        with transaction.atomic():
            Page.objects.all().delete()
            for data in DEMO_PAGES:
                data = dict(data)
                image = data.pop("image")
                posted_at = now - timedelta(days=data.pop("days_ago"), hours=data.pop("hours_ago"))
                page = Page(**data)
                with open(DEMO_IMAGE_DIR / image, "rb") as f:
                    page.picture.save(UPLOAD_PREFIX + image, File(f), save=False)
                page.save()
                # 出品日時がばらけるように上書き（auto_now 系は update で回避）
                Page.objects.filter(pk=page.pk).update(created_at=posted_at, updated_at=posted_at)

        self.stdout.write(self.style.SUCCESS(
            f"既存データ {count} 件を削除し、デモデータ {len(DEMO_PAGES)} 件を投入しました。"
        ))

    def _remove_previous_demo_files(self):
        """以前の seed_demo で保存した画像だけを削除する（ユーザーがアップした画像は残す）。"""
        upload_dir = Path(settings.MEDIA_ROOT) / Page._meta.get_field("picture").upload_to
        if upload_dir.exists():
            for path in upload_dir.glob(UPLOAD_PREFIX + "*"):
                path.unlink()
