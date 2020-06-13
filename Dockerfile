FROM python:3.8

WORKDIR /codelet

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY server.py app/config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP server.py

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]