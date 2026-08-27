"""
小売店の売上データを生成するスクリプト（ポートフォリオ用の疑似データ）。

名古屋市内で複数店舗・複数部門を展開する仮想の小売店をイメージし、
部門別・商品カテゴリ別・日次の売上データを生成します。

乱数シードを固定しているため、再現可能です。
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RANDOM_SEED = 7
rng = np.random.default_rng(RANDOM_SEED)

DEPARTMENTS = {
    # 部門名: (基準日販, 季節変動の強さ)
    "食品": {"base": 85000, "seasonality": 0.15},
    "日用品": {"base": 42000, "seasonality": 0.05},
    "衣料品": {"base": 38000, "seasonality": 0.35},
    "雑貨": {"base": 26000, "seasonality": 0.20},
}

PRODUCTS = {
    # 商品名: (所属部門, 基準日販, トレンド係数)
    "野菜セット": ("食品", 12000, 1.00),
    "お弁当": ("食品", 18000, 1.05),
    "洗剤": ("日用品", 9000, 0.98),
    "ティッシュ": ("日用品", 7000, 1.00),
    "Tシャツ": ("衣料品", 8000, 1.10),
    "冬物コート": ("衣料品", 6000, 1.00),
    "食器": ("雑貨", 5000, 1.02),
    "文房具": ("雑貨", 4000, 0.99),
}

START_DATE = datetime(2026, 1, 1)
N_DAYS = 180  # 半年分


def seasonal_factor(date, strength):
    """月による季節変動（正弦波で簡易表現）。"""
    month_angle = 2 * np.pi * (date.month - 1) / 12
    return 1.0 + strength * np.sin(month_angle + np.pi / 3)


def generate_department_sales():
    records = []
    for i in range(N_DAYS):
        date = START_DATE + timedelta(days=i)
        for dept, params in DEPARTMENTS.items():
            factor = seasonal_factor(date, params["seasonality"])
            weekday_factor = 1.25 if date.weekday() >= 5 else 1.0  # 週末は売上増
            amount = params["base"] * factor * weekday_factor * rng.normal(1.0, 0.08)
            records.append(
                {"date": date.strftime("%Y-%m-%d"), "department": dept, "amount": int(max(amount, 0))}
            )
    return pd.DataFrame(records)


def generate_product_sales():
    records = []
    for i in range(N_DAYS):
        date = START_DATE + timedelta(days=i)
        for product, (dept, base, trend) in PRODUCTS.items():
            # trend: 1.0超で緩やかに増加、未満で減少
            days_factor = trend ** (i / 30)  # 月単位で複利的に効かせる
            dept_strength = DEPARTMENTS[dept]["seasonality"]
            factor = seasonal_factor(date, dept_strength * 0.7)
            weekday_factor = 1.2 if date.weekday() >= 5 else 1.0
            amount = base * factor * weekday_factor * days_factor * rng.normal(1.0, 0.12)
            records.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "product": product,
                    "department": dept,
                    "amount": int(max(amount, 0)),
                }
            )
    return pd.DataFrame(records)


if __name__ == "__main__":
    dept_df = generate_department_sales()
    product_df = generate_product_sales()

    dept_df.to_csv("data/department_sales.csv", index=False, encoding="utf-8-sig")
    product_df.to_csv("data/product_sales.csv", index=False, encoding="utf-8-sig")

    print("department_sales:", dept_df.shape)
    print("product_sales   :", product_df.shape)
