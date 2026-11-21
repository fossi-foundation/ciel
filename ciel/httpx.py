from typing import TYPE_CHECKING

try:
    from httpx2 import (
        Client,
        Headers,
        HTTPError,
        HTTPStatusError,
        NetworkError,
        Response,
    )
except ImportError:
    if not TYPE_CHECKING:
        from httpx import Client, Headers, HTTPStatusError, NetworkError, Response

__all__ = [
    "Client",
    "HTTPError",
    "HTTPStatusError",
    "Headers",
    "NetworkError",
    "Response",
]
