import glob
import string
import datetime
import json
import os
import subprocess

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import dotenv
import matplotlib.pyplot as plt
import pandas as pd

dotenv.load_dotenv()

spread_id = "1ti4e4rHKi_6WV4pYccY1YvX0t17dgyXwSBdoiZH2i8M"

last_n_days = 5
top_n_words = 10
rolling_days = 4

TITLE_PUNCTUATION = "„”–" + string.punctuation

punctuation_removal = str.maketrans({p: "" for p in TITLE_PUNCTUATION})

scope = ["https://spreadsheets.google.com/feeds"]
d = json.load(open("creds.json"))
d["private_key"] = os.environ["GSPREAD_PRIVATE_KEY"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(d, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(spread_id).sheet1

title_df = pd.DataFrame(sheet.get_all_records()).assign(
    dtime=lambda df: df["time"].pipe(pd.to_datetime)
)


def get_word_frac(s):
    return (
        s.str.lower()
        .str.translate(punctuation_removal)
        .str.split()
        .pipe(lambda s: pd.Series(s.sum()).value_counts(normalize=True))
        .rename("words")
    )


def get_relative_prevelance(_df):
    return (
        _df.groupby("site")
        .apply(lambda df: df["title"].pipe(get_word_frac))
        .reset_index()
        .rename(columns={"level_1": "word"})
        .pivot_table(index="word", columns="site", values="words")
        .fillna(0)
        .pipe(lambda df: df.apply(lambda s: s - df.drop(s.name, axis=1).mean(axis=1)))
    )


def plot_most(s, end_date, row_id):
    ax = (
        s.nlargest(10)
        .iloc[::-1]
        .plot.barh(title=f"{s.name} - {end_date}", figsize=(12, 7))
    )
    plt.xlabel("relative frequency")
    plt.savefig(f"docs/{row_id} - {s.name.translate(punctuation_removal)}.png")


os.makedirs("docs", exist_ok=True)

for mday in range(last_n_days):
    act_df = title_df.loc[
        lambda df: (
            df["dtime"]
            > (datetime.datetime.now() - datetime.timedelta(days=mday + rolling_days))
        )
        & (df["dtime"] <= (datetime.datetime.now() - datetime.timedelta(days=mday))),
        :,
    ]

    act_df.pipe(get_relative_prevelance).apply(
        plot_most, end_date=act_df["dtime"].dt.date.max(), row_id=mday + 1
    )

pictures = glob.glob("docs/*.png")

html_raw = "".join([f"<img src='{p.split('/')[-1]}'></img>" for p in sorted(pictures)])

with open("docs/index.html", "w") as fp:
    fp.write(html_raw)

