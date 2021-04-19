accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sµs'  # noqa: E501
bind = "0.0.0.0:8000"
workers = 4
