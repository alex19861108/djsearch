from __future__ import absolute_import, unicode_literals

import pymysql
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
# from gevent import monkey

from djsearch import settings
from djsearch.celery import app as celery_app

# monkey.patch_all()

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

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
__all__ = ('celery_app',)
