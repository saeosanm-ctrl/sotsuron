import pandas as pd
import glob
import os
from datetime import datetime

# データ取得日
today = datetime.now().strftime("%Y%m%d")

files = glob.glob("*.csv")
print("対象ファイル:", files)

# =========================
# 日付ごとに分ける箱
# =========================
date_groups = {}

for f in files:
    df = pd.read_csv(f)

    # ファイル名例：fukuoka_20260414.csv
    parts = os.path.basename(f).replace(".csv", "").split("_")
    area = parts[0]
    date = parts[1]

    df["area"] = area

    # 日付ごとにまとめる
    if date not in date_groups:
        date_groups[date] = []

    date_groups[date].append(df)

# =========================
# 日付ごとにマージして保存
# =========================
for date, df_list in date_groups.items():
    merged = pd.concat(df_list, ignore_index=True)

    filename = f"merged_{today}_{date}.csv"
    merged.to_csv(filename, index=False, encoding="utf-8-sig")

    print("保存:", filename, "件数:", len(merged))
