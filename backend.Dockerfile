FROM python:3.7.5-slim-buster

WORKDIR /snake_eyes

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

COPY requirements.txt /tmp/requirements.txt

RUN pip install --requirement /tmp/requirements.txt

COPY . .

RUN pip install --editable /snake_eyes

CMD gunicorn --config "python:config.gunicorn" "snake_eyes.app:create_app()"
