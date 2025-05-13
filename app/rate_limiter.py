from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

# Initialize limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])

# This function can be used to add rate limiting to specific routes or globally.
# To apply globally, add it as middleware in main.py
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Example of how to use it as a dependency on a route:
# from fastapi import Depends
# from .rate_limiter import limiter
# @app.get("/limited", dependencies=[Depends(limiter.limit("5 per minute"))])
# async def limited_route():
#     return {"message": "This route is rate-limited."}


