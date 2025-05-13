from fastapi import FastAPI
from starlette.requests import Request # Required for rate limiter state
from .database import engine, Base
from .routers import authentication, documents, audit
from .storage import minio_client, MINIO_BUCKET_NAME, create_bucket_if_not_exists
from .rate_limiter import limiter, _rate_limit_exceeded_handler # Import rate limiter
from slowapi.errors import RateLimitExceeded # Import RateLimitExceeded

# Create database tables
Base.metadata.create_all(bind=engine)

# Create MinIO bucket
try:
    create_bucket_if_not_exists(minio_client, MINIO_BUCKET_NAME)
except Exception as e:
    print(f"Could not create or verify MinIO bucket: {e}")

app = FastAPI(
    title="DocVerify API",
    description="API for digital document verification, fraud prevention, and intellectual property protection.",
    version="0.1.0"
)

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(authentication.router)
app.include_router(documents.router)
app.include_router(audit.router)

@app.get("/")
async def root():
    return {"message": "Welcome to DocVerify API! See /docs for API documentation."}

# Apply rate limiting to all routes or specific ones as needed.
# For example, to apply to all, you might use middleware or apply to each router.
# For now, individual routes can use Depends(limiter.limit("...")) if needed.

