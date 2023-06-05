import logging

from sqlalchemy import (
    Column,
    Date,
    Integer,
    String,
    and_,
    create_engine,
    extract,
    func,
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker

logging.info("Connecting to database.")
engine = create_engine("sqlite:///db.sqlite")
Base = declarative_base()


class Weather(Base):
    __tablename__ = "weather"
    dt = Column("dt", Date, nullable=False, primary_key=True)
    city = Column("city", String(255), nullable=False, primary_key=True)
    day_temperature = Column("day_temperature", Integer)
    day_pressure = Column("day_pressure", Integer)
    day_wind = Column("day_wind", Integer)
    night_temperature = Column("night_temperature", Integer)
    night_pressure = Column("night_pressure", Integer)
    night_wind = Column("night_wind", Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def day(self):
        return {
            "temperature": self.day_temperature,
            "pressure": self.day_pressure,
            "wind": self.day_wind,
        }

    def night(self):
        return {
            "temperature": self.night_temperature,
            "pressure": self.night_pressure,
            "wind": self.night_wind,
        }

    def avg(self):
        return {
            "temperature": (self.day_temperature + self.night_temperature) / 2,
            "pressure": (self.day_pressure + self.night_pressure) / 2,
            "wind": (self.day_wind + self.night_wind) / 2,
        }


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


def get_max_dt(city):
    query = func.max(select(Weather.dt).scalar_subquery().where(Weather.city == city))
    with Session() as session:
        return session.execute(query).fetchone()[0]


def upsert(df) -> None:
    with Session() as session:
        for row in df.to_dict("records"):
            logging.info(f"Writing {row} to dadabase.")
            session.merge(Weather(**row))
            session.commit()


def get_day_data(city, dt):
    query = select(Weather).where(and_(Weather.city == city, Weather.dt == dt))
    with Session() as session:
        result = session.execute(query).fetchone()
        if result:
            return result[0]


def get_month_data(city, year, month, agg):
    aggs = {
        "avg": func.avg,
        "mode": func.mode,
        "min": func.min,
        "max": func.max,
    }
    agg_func = aggs[agg]

    query = (
        select(
            agg_func(Weather.day_temperature),
            agg_func(Weather.day_pressure),
            agg_func(Weather.day_wind),
            agg_func(Weather.night_temperature),
            agg_func(Weather.night_pressure),
            agg_func(Weather.night_wind),
        )
        .where(
            and_(
                Weather.city == city,
                extract("year", Weather.dt) == year,
                extract("month", Weather.dt) == month,
            )
        )
        .group_by()
    )

    with Session() as session:
        result = session.execute(query).fetchone()
        if result:
            response = {}
            for key, value in zip(
                [
                    "day_temperature",
                    "day_pressure",
                    "day_wind",
                    "nigth_temperature",
                    "nigth_pressure",
                    "nigth_wind",
                ],
                result,
            ):
                response[key] = value

            return response
