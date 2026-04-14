import pandas as pd
import glob
import os
from datetime import datetime

# =========================
# データ取得日（今日）
# =========================
today = datetime.utcnow()+timedelta(hours=9).strftime("%Y%m%d_%H%M")

# =========================
# CSV取得
# =========================
files = glob.glob("*.csv")
print("対象ファイル:", files)

# =========================
# 日付ごとにまとめる
# =========================
date_groups = {}

for f in files:
    try:
        df = pd.read_csv(f)

        # 空ファイル対策
        if df.empty:
            print("スキップ（空）:", f)
            continue

    except:
        print("スキップ（読込失敗）:", f)
        continue

    # ファイル名例：fukuoka_20260414.csv
    basename = os.path.basename(f).replace(".csv", "")
    parts = basename.split("_")

    # 念のためチェック
    if len(parts) < 2:
        print("スキップ（形式不正）:", f)
        continue

    area = parts[0]
    date = parts[1]

    # 地域カラム追加（念のため）
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

print("=== 完了 ===")
