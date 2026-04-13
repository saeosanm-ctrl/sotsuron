import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# =========================
# 日付（明日宿泊想定）
# =========================
today = datetime.now()
checkin = (today + timedelta(days=1)).strftime("%Y-%m-%d")
checkout = (today + timedelta(days=2)).strftime("%Y-%m-%d")

# =========================
# APIキー（Secretsから取得）
# =========================
APP_ID = os.environ["RAKUTEN_APP_ID"]
ACCESS_KEY = os.environ["RAKUTEN_ACCESS_KEY"]

# =========================
# API設定
# =========================
url = "https://openapi.rakuten.co.jp/engine/api/Travel/VacantHotelSearch/20170426"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

params = {
    "format": "json",
    "checkinDate": checkin,
    "checkoutDate": checkout,
    "largeClassCode": "japan",
    "middleClassCode": "hukuoka",
    "smallClassCode": "fukuoka",
    "applicationId": APP_ID,
    "accessKey": ACCESS_KEY
}

# =========================
# API実行
# =========================
res = requests.get(url, params=params, headers=headers)
data = res.json()

rows = []

for item in data.get("hotels", []):
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

    rows.append(row)

# =========================
# CSV保存
# =========================
df = pd.DataFrame(rows)

filename = f"fukuoka_{today.strftime('%Y%m%d')}.csv"
df.to_csv(filename, index=False, encoding="cp932")

print("完了:", filename)
print(df.head())
