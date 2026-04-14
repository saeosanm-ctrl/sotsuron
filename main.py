import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

AREA = os.environ["AREA"]

APP_ID = os.environ["RAKUTEN_APP_ID"]
ACCESS_KEY = os.environ["RAKUTEN_ACCESS_KEY"]

url = "https://openapi.rakuten.co.jp/engine/api/Travel/VacantHotelSearch/20170426"

headers = {
    "Referer": "https://example.com",
    "Origin": "https://example.com",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

# =========================
# ★ 取得日（3パターン）
# =========================
today = datetime.now()

target_days = [
    today,
    today + timedelta(days=3),
    today + timedelta(days=7)
]

# =========================
# 日付ループ
# =========================
for target in target_days:

    checkin = target.strftime("%Y-%m-%d")
    checkout = (target + timedelta(days=1)).strftime("%Y-%m-%d")
    date_str = target.strftime("%Y%m%d")

    print(f"===== {AREA} / {checkin} =====")

    all_rows = []
    page = 1

    while True:
        print(f"ページ: {page}")

        retry_count = 0

        while True:
            res = requests.get(url, params={
                "format": "json",
                "checkinDate": checkin,
                "checkoutDate": checkout,
                "largeClassCode": "japan",
                "middleClassCode": "hukuoka",
                "smallClassCode": AREA,
                "applicationId": APP_ID,
                "accessKey": ACCESS_KEY,
                "hits": 30,
                "page": page
            }, headers=headers)

            # =========================
            # ★ 429対策（強化版）
            # =========================
            if res.status_code == 429:
                retry_count += 1
                wait_time = 10 * retry_count
                print(f"429エラー → {wait_time}秒待機（{retry_count}回目）")
                time.sleep(wait_time)

                # 3回以上失敗したら諦める
                if retry_count >= 3:
                    print("429多発 → ページスキップ")
                    break
                continue

            break

        # 429でスキップされた場合
        if res.status_code == 429:
            break

        data = res.json()

        print("ステータス:", res.status_code)
        print("取得件数:", len(data.get("hotels", [])))

        hotels = data.get("hotels", [])

        if len(hotels) == 0:
            break

        for item in hotels:
            hotel_blocks = item["hotel"]
            row = {}

            for block in hotel_blocks:

                if "hotelBasicInfo" in block:
                    for k, v in block["hotelBasicInfo"].items():
                        row[f"basic_{k}"] = v

                if "roomInfo" in block:
                    for room in block["roomInfo"]:

                        if "roomBasicInfo" in room:
                            for k, v in room["roomBasicInfo"].items():
                                row[f"room_{k}"] = v

                        if "dailyCharge" in room:
                            for k, v in room["dailyCharge"].items():
                                row[f"charge_{k}"] = v

            row["date"] = checkin
            row["area"] = AREA

            all_rows.append(row)

        page += 1

        # =========================
        # ★ ページ間待機（強化）
        # =========================
        time.sleep(3)

        # =========================
        # ★ ページ上限10
        # =========================
        if page > 10:
            print("ページ上限で終了")
            break

    # =========================
    # CSV保存
    # =========================
    if len(all_rows) == 0:
        print("データなし:", checkin)
        continue

    df = pd.DataFrame(all_rows)

    filename = f"{AREA}_{date_str}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print("保存:", filename, "件数:", len(df))
