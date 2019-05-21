import os
import requests
import logging
from urllib.parse import urljoin
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def configure_logging(debug=False, fp=None):
    root = logging.getLogger()
    root.handlers.clear()

    fmt = logging.Formatter(
        fmt='%(asctime)s %(levelname)s (%(name)s) %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(fmt)
    h.addFilter(lambda x: x.levelno <= logging.INFO)

    h2 = logging.StreamHandler(sys.stderr)
    h2.setFormatter(fmt)
    h2.addFilter(lambda x: x.levelno > logging.INFO)

    root.addHandler(h)
    root.addHandler(h2)

    if fp:
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        fileHandler = logging.FileHandler(fp)
        fileHandler.setFormatter(fmt)
        root.addHandler(fileHandler)

    if debug:
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)

def get_host():
    host = os.environ.get('HOST')
    assert host, 'host not set'
    host = host.rstrip('/')
    return host

def get_client_id():
    value = os.environ.get('CLIENT-ID')
    assert value, 'client id not set'
    return value

def get_client_secret():
    value = os.environ.get('CLIENT-SECRET')
    assert value, 'client secret not set'
    return value

def url(name):
    return '{}/{}'.format(get_host(), name.lstrip('/'))

def touch(path):
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)

def get_token(client_id=None, client_secret=None):
    r = post(
        url=url('/api/3.1/login'),
        data={
            'client_id': client_id or get_client_id(),
            'client_secret': client_secret or get_client_secret()
        }
    )
    assert r.status_code in range(200,300), r.text
    return r.json()['access_token']

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token=None):
        self._token = token

    @property
    def token(self):
        if not self._token:
            logger.info('provisioning bearer token')
            self._token = get_token()
        return self._token

    def __eq__(self, other):
        return self.token == getattr(other, 'token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r

def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None):

    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

DEFAULT_TIMEOUT=5

def add_timeout(kwargs):
    return dict(dict(timeout=DEFAULT_TIMEOUT), **kwargs)

def post(*args, **kwargs):
    new_kwargs = add_timeout(kwargs)
    return requests_retry_session().post(*args, **new_kwargs)

def get(*args, **kwargs):
    new_kwargs = add_timeout(kwargs)
    return requests_retry_session().get(*args, **new_kwargs)

def delete(*args, **kwargs):
    new_kwargs = add_timeout(kwargs)
    return requests_retry_session().delete(*args, **new_kwargs)
