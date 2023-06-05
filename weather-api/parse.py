import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from database import get_max_dt, upsert
from parse_month import get_month_data

logging.basicConfig(
    level=logging.INFO,
    filename="log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
)

cities = {"msk": "4368", "spb": "4079", "sochi": "5233"}
start_date = date(2000, 1, 1)
end_date = date.today()
month_delta = relativedelta(months=1)

for city, code in cities.items():
    dt = start_date
    max_dt = get_max_dt(city)

    if max_dt:
        dt = max_dt

    while dt <= end_date:
        logging.info(f"Parsing weather data for {dt}")
        df = get_month_data(city, code, dt.year, dt.month)
        if df is not None:
            upsert(df)
        dt += month_delta
