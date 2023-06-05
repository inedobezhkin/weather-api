import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}


def get_soup(url):
    with requests.get(url, headers=headers) as r:
        return BeautifulSoup(r.text, features="lxml")


def get_month_data(city, code, year, month):
    soup = get_soup(f"http://www.gismeteo.ru/diary/{code}/{year}/{month}/")
    table = soup.find("table")

    if not table:
        return None

    df = pd.read_html(str(table))[0]
    df.columns = [
        "day",
        "day_temperature",
        "day_pressure",
        "day_cloudiness",
        "day_features",
        "day_wind",
        "night_temperature",
        "night_pressure",
        "night_cloudiness",
        "night_features",
        "night_wind",
    ]
    df = df.iloc[:-2]

    df["city"] = city
    df["year"] = year
    df["month"] = month
    df["dt"] = pd.to_datetime(df[["year", "month", "day"]])

    df = df[
        [
            "dt",
            "city",
            "day_temperature",
            "day_pressure",
            "day_wind",
            "night_temperature",
            "night_pressure",
            "night_wind",
        ]
    ]

    cols = df.columns[2:]
    for col in cols:
        df[col] = df[col].str.extract("(\d+)")
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(int)

    return df
