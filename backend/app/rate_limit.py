"""Shared slowapi limiter.

Defined in its own module so both the routes (which decorate endpoints) and
main.py (which registers the limiter + error handler) can import it without a
circular dependency.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
