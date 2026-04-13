import requests
import csv
from datetime import datetime

import requests

url = "https://openapi.rakuten.co.jp/engine/api/Travel/VacantHotelSearch/20170426"

headers = {
    "Referer": "https://example.com",
    "Origin":"https://example.com",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

params = {
    "format": "json",
    "checkinDate": "2026-04-24",
    "checkoutDate": "2026-04-25",
    "largeClassCode": "japan",
    "middleClassCode": "hukuoka",
    #"smallClassCode": "fukuoka",
    #"smallClassCode": "seibu",
    #"smallClassCode": "kitakyusyu",
    #"smallClassCode": "chikuzen",
    #"smallClassCode": "kurume",
    #"smallClassCode": "buzen",
    #"smallClassCode": "chikugo",
    "applicationId": "b31dbdc1-ae6a-4086-a767-b270a1c98a7e",
    "accessKey": "pk_kA9mrZ7CHdQWETMgJIal0X2MbQYzZ3xhfYIfw1JwXlR"
}


res = requests.get(url, params=params, headers=headers)
data = res.json()

rows = []

for item in data["hotels"]:
    hotel_blocks = item["hotel"]

    row = {}

    for block in hotel_blocks:

        # =========================
        # hotelBasicInfo
        # =========================
        if "hotelBasicInfo" in block:
            for k, v in block["hotelBasicInfo"].items():
                row[f"basic_{k}"] = v

        # =========================
        # roomInfo（複数要素）
        # =========================
        if "roomInfo" in block:
            for room in block["roomInfo"]:

                # ---- roomBasicInfo ----
                if "roomBasicInfo" in room:
                    for k, v in room["roomBasicInfo"].items():
                        row[f"room_{k}"] = v

                # ---- dailyCharge ----
                if "dailyCharge" in room:
                    for k, v in room["dailyCharge"].items():
                        row[f"charge_{k}"] = v

    rows.append(row)

import pandas as pd

# ========= ③ DataFrame化 =========
df = pd.DataFrame(rows)

# ========= ④ CSV保存 =========
df.to_csv("chikugo_260413.csv", index=False, encoding="cp932")

print("完了")
print(df.head())
