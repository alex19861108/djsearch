import pymysql
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from djsearch import settings

# mysql
pymysql.install_as_MySQLdb()

# sentry_dsn
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)