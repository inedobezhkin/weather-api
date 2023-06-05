import logging

from flask import Flask, abort, request
from waitress import serve

from database import get_day_data, get_month_data

logging.basicConfig(
    level=logging.INFO,
    filename="log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
)

app = Flask(__name__)


@app.route("/api/weather/daily", methods=["GET"])
def get_weather_daily():
    args = request.args

    logging.info(f"Get daily weather with {args} args.")

    city = args.get("city")
    dt = args.get("dt")
    data_type = args.get("type", "day")

    day_data = get_day_data(city, dt)

    if not day_data:
        abort(404)

    if data_type == "day":
        return day_data.day()
    elif data_type == "night":
        return day_data.night()
    elif data_type == "avg":
        return day_data.avg()
    else:
        abort(404)


@app.route("/api/weather/monthly", methods=["GET"])
def get_weather_avg_monthly():
    args = request.args

    logging.info(f"Get monthly weather with {args} args.")

    city = args.get("city")
    year = args.get("year")
    month = args.get("month")
    agg = args.get("agg", "avg")

    month_data = get_month_data(city, year, month, agg)
    print(month_data)
    if not month_data["day_temperature"]:
        abort(404)

    return month_data


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
