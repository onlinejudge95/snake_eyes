from os import environ


accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sµs'  # noqa: E501
bind = f"0.0.0.0:{environ.get("PORT", 8000)}"
workers = int(environ.get("WORKER_COUNT"))
