import httpx
from supabase import Client, create_client

from backend.config import settings


# The Supabase Python client enables HTTP/2 by default. On some Windows setups,
# that leads to a non-blocking socket error before the request reaches PostgREST.
# Force HTTP/2 off for the app so requests behave reliably in this environment.
_original_httpx_client_init = httpx.Client.__init__
_original_httpx_async_client_init = httpx.AsyncClient.__init__


def _patched_httpx_client_init(self, *args, http2=None, **kwargs):
    if http2 is True:
        http2 = False
    return _original_httpx_client_init(self, *args, http2=http2, **kwargs)


def _patched_httpx_async_client_init(self, *args, http2=None, **kwargs):
    if http2 is True:
        http2 = False
    return _original_httpx_async_client_init(self, *args, http2=http2, **kwargs)


httpx.Client.__init__ = _patched_httpx_client_init
httpx.AsyncClient.__init__ = _patched_httpx_async_client_init

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def get_supabase() -> Client:
    return supabase
