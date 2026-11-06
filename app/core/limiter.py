from slowapi import Limiter
from slowapi.util import get_remote_address

"""
This uses an in-memory store; current limitations:
- Counters reset when the Render instance restarts or spins down.
- Limits are per running process, not shared across multiple instances.
"""

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
)
