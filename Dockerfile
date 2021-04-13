# FROM python:3.7.5-slim-buster as base
FROM python:3.7.5-slim-buster

# WORKDIR /wheels
WORKDIR /snake_eyes

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

COPY requirements.txt /tmp/requirements.txt

# RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels --requirement /tmp/requirements.txt
RUN pip install --requirement /tmp/requirements.txt

# FROM python:3.7.5-slim-buster

# WORKDIR /snake_eyes

# RUN apt-get update && apt-get install -qq -y \
#   build-essential libpq-dev --no-install-recommends

# COPY --from=base /wheels /wheels

# RUN pip install --no-cache-dir /wheels/*

COPY . .

RUN pip install --editable /snake_eyes

CMD ["bash", "/snake_eyes/bin/entrypoint.sh"]
