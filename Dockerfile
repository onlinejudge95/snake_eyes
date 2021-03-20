FROM python:3.9.0-slim as base

WORKDIR /wheels

COPY requirements.txt /tmp/requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels --requirement /tmp/requirements.txt

FROM python:3.9.0-slim

WORKDIR /snake_eyes

COPY --from=base /wheels /wheels

RUN pip install --no-cache-dir /wheels/*

COPY . .

CMD ["bash", "/snake_eyes/bin/entrypoint.sh"]
