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
# ★ 取得する日（ここが変更点）
# =========================
today = datetime.now()

target_days = [
    today,                         # 当日
    today + timedelta(days=3),     # 3日後
    today + timedelta(days=7)      # 1週間後
]

# =========================
# 日付ごとにループ
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

        params = {
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
        }

        res = requests.get(url, params=params, headers=headers)
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

            # ★ 重要：日付と地域
            row["date"] = checkin
            row["area"] = AREA

            all_rows.append(row)

        page += 1
        time.sleep(1)

        if page > 10:
            print("強制終了")
            break

    # =========================
    # ★ 日付ごとに保存
    # =========================
    df = pd.DataFrame(all_rows)

    filename = f"{AREA}_{date_str}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print("保存:", filename, "件数:", len(df))
