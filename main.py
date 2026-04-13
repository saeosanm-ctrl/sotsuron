import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# =========================
# 日付設定（明日宿泊）
# =========================
today = datetime.now()
checkin = (today + timedelta(days=1)).strftime("%Y-%m-%d")
checkout = (today + timedelta(days=2)).strftime("%Y-%m-%d")

# =========================
# APIキー（GitHub Secrets）
# =========================
APP_ID = os.environ["RAKUTEN_APP_ID"]
ACCESS_KEY = os.environ["RAKUTEN_ACCESS_KEY"]

# =========================
# 地域リスト（7地域）
# =========================
areas = ["fukuoka"]

# =========================
# API設定
# =========================
url = "https://openapi.rakuten.co.jp/engine/api/Travel/VacantHotelSearch/20170426"

headers = {
    "Referer": "https://example.com",
    "Origin": "https://example.com",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

all_rows = []

# =========================
# 地域ごとループ
# =========================
for area in areas:
    print(f"===== 地域: {area} =====")

    page = 1

    while True:
        print(f"{area} ページ: {page}")

        params = {
            "format": "json",
            "checkinDate": checkin,
            "checkoutDate": checkout,
            "largeClassCode": "japan",
            "middleClassCode": "hukuoka",
            "smallClassCode": area,
            "applicationId": APP_ID,
            "accessKey": ACCESS_KEY,
            "hits": 100,   # 最大件数
            "page": page
        }

        res = requests.get(url, params=params, headers=headers)
        data = res.json()

        hotels = data.get("hotels", [])

        print("取得件数:", len(hotels))

        # データがなければ終了
        if len(hotels) == 0:
            break

        # =========================
        # データ整形
        # =========================
        for item in hotels:
            hotel_blocks = item["hotel"]
            row = {}

            # 地域情報（超重要）
            row["area"] = area

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

            all_rows.append(row)

        page += 1

        # API制限対策
        time.sleep(1)

# =========================
# CSV保存
# =========================
df = pd.DataFrame(all_rows)

filename = f"fukuoka_all_{today.strftime('%Y%m%d')}.csv"
df.to_csv(filename, index=False, encoding="cp932")

print("完了:", filename)
print("総件数:", len(df))
print(df.head())
