FROM python:3.11.3-slim-bullseye

WORKDIR /usr/src/

COPY ./src .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./scripts .
RUN chmod 0644 run-every-day
RUN chmod a+x run.sh

CMD [ "./run.sh" ]