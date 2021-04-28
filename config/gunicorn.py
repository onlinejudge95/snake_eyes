from os import environ


accesslog = "-"
access_log_format = (
    "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in" "%(D)sµs"
)
bind = f"0.0.0.0:{environ.get('PORT', 8000)}"
workers = 4
