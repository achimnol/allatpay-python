# Django settings for apsys project.

import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# .... many stuffs ....

# You may have to modify this to your environment.
# This is Ubuntu default.
CA_CERTS_PATH = '/etc/ssl/certs/ca-certificates.crt'

PAYMENT_SHOPID = {
    u'DOMESTIC': 'test',
    u'ABROAD': 'test',
}
PAYMENT_CROSSKEY = {
    u'DOMESTIC': '12345',
    u'ABROAD': '12345',
}

try:
    from local_settings import *
except ImportError:
    pass
