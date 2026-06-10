"""Steamのプレイデータからプレイ時間の円グラフを生成するスクリプト。

環境変数 STEAM_API_KEY, STEAM_ID を使ってSteam Web APIから
所持ゲーム一覧を取得し、プレイ時間上位のゲームを円グラフ画像として
assets/steam-playtime.png に保存する。
"""

import os
import sys

import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt

API_KEY = os.environ["STEAM_API_KEY"]
STEAM_ID = os.environ["STEAM_ID"]
OUTPUT_PATH = "assets/steam-playtime.png"
TOP_N = 8

API_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"


def fetch_games():
    params = {
        "key": API_KEY,
        "steamid": STEAM_ID,
        "format": "json",
        "include_appinfo": "true",
        "include_played_free_games": "true",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["response"].get("games", [])


def build_chart(games):
    games = [g for g in games if g.get("playtime_forever", 0) > 0]
    games.sort(key=lambda g: g["playtime_forever"], reverse=True)

    top = games[:TOP_N]
    others = games[TOP_N:]

    labels = [g["name"] for g in top]
    hours = [g["playtime_forever"] / 60 for g in top]

    if others:
        other_hours = sum(g["playtime_forever"] for g in others) / 60
        labels.append("その他")
        hours.append(other_hours)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(hours, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Steam プレイ時間")
    ax.axis("equal")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.savefig(OUTPUT_PATH, bbox_inches="tight")


def main():
    games = fetch_games()
    if not games:
        print("プレイ時間のあるゲームが見つかりませんでした", file=sys.stderr)
        sys.exit(1)
    build_chart(games)


if __name__ == "__main__":
    main()
