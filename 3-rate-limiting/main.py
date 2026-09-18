from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from pathlib import Path
import logging
import time
import uuid


# ============================================================
# 1. Configure Python logging
# ============================================================
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/app.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)
app = FastAPI(
    title="FastAPI Rate Limiting Demo",
    description="Comprehensive SlowAPI rate limiting examples",
    version="1.0.0",
)

logger = logging.getLogger("api")
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware that logs every HTTP request.

    It records:
    - HTTP method
    - URL/path
    - client IP
    - request ID
    - response status code
    - execution time
    """

    # --------------------------------------------------------
    # Generate unique ID for this request
    # --------------------------------------------------------

    request_id = str(uuid.uuid4())

    # --------------------------------------------------------
    # Get request information
    # --------------------------------------------------------

    method = request.method
    path = request.url.path

    # --------------------------------------------------------
    # Get client IP
    # --------------------------------------------------------

    client_ip = request.client.host if request.client else "unknown"


    # --------------------------------------------------------
    # Log incoming request
    # --------------------------------------------------------

    logger.info(
        f"REQUEST | "
        f"id={request_id} | "
        f"method={method} | "
        f"path={path} | "
        f"client={client_ip}"
    )
    # --------------------------------------------------------
        # Start timer
        # --------------------------------------------------------
    
    start_time = time.perf_counter()
    
    try:

        # ----------------------------------------------------
        # Pass request to next middleware / endpoint
        # ----------------------------------------------------

        response = await call_next(request)

    except Exception:

        # ----------------------------------------------------
        # Calculate execution time even if an error happens
        # ----------------------------------------------------

        process_time = time.perf_counter() - start_time

        logger.exception(
            f"ERROR | "
            f"id={request_id} | "
            f"method={method} | "
            f"path={path} | "
            f"client={client_ip} | "
            f"time={process_time:.4f}s"
        )

        raise

    # --------------------------------------------------------
    # Calculate execution time
    # --------------------------------------------------------

    process_time = time.perf_counter() - start_time

    # --------------------------------------------------------
    # Add request ID to response
    # --------------------------------------------------------

    response.headers["X-Request-ID"] = request_id

    # --------------------------------------------------------
    # Log response
    # --------------------------------------------------------

    logger.info(
        f"RESPONSE | "
        f"id={request_id} | "
        f"method={method} | "
        f"path={path} | "
        f"status={response.status_code} | "
        f"time={process_time:.4f}s"
    )

    return response




# ============================================================
# BASIC RATE LIMITER
# ============================================================


limiter = Limiter(
    key_func=get_remote_address,

  

    # Default limits applied to endpoints
    # that don't define their own limits.
    default_limits=[
        "100/minute"
    ],
)


# Register SlowAPI limiter
app.state.limiter = limiter

# Register the 429 exception handler
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# Middleware required by SlowAPI
app.add_middleware(SlowAPIMiddleware)


# ============================================================
#  BASIC ENDPOINT
# ============================================================

@app.get("/")
async def root():

    return {
        "message": "FastAPI Rate Limiting Demo"
    }


# ============================================================
# GLOBAL / DEFAULT RATE LIMIT
# ============================================================

@app.get("/default-limit")
async def default_limit():

    """
    This endpoint uses the default limit:

        100 requests/minute

    because we configured:

        default_limits=["100/minute"]

    The limit is based on the remote IP address.
    """

    return {
        "message": "This endpoint uses the default rate limit"
    }


# ============================================================
# ENDPOINT-SPECIFIC RATE LIMIT
# ============================================================

@app.get("/expensive-operation")
@limiter.limit("5/minute")
async def expensive_operation(request: Request):

    """
    Only 5 requests/minute per remote address.

    Important:
    request: Request

    should be included in the endpoint when using
    SlowAPI decorators.
    """

    return {
        "message": "Expensive operation executed"
    }




# ============================================================
# MULTIPLE RATE LIMITS
# ============================================================

@app.get("/multiple-limits")
@limiter.limit("5/minute")
@limiter.limit("100/day")
async def multiple_limits(request: Request):

    """
    Multiple limits can protect the same endpoint.

    The client must satisfy BOTH:

        5 requests/minute

    AND

        100 requests/day

    Example:

    Request 1  -> OK
    Request 2  -> OK
    ...
    Request 5  -> OK
    Request 6  -> 429

    Even if the minute window resets,
    the client can still hit the daily limit.
    """

    return {
        "message": "Endpoint with multiple limits"
    }


# ============================================================
# CUSTOM KEY FUNCTION
# ============================================================

def get_client_ip(request: Request) -> str:
    """
    Custom key function.

    Instead of using SlowAPI's built-in
    get_remote_address(), we explicitly
    access the remote client IP.
    """

    if request.client:
        return request.client.host

    return "unknown"


ip_limiter = Limiter(
    key_func=get_client_ip,
    headers_enabled=True,
)


# ============================================================
# USER-LEVEL RATE LIMITING
# ============================================================

def get_user_identifier(request: Request) -> str:
    """
    Rate limit based on USER instead of IP.

    For demonstration purposes we use:

        X-User-ID

    header.

    Example:

        X-User-ID: user_123

    Production systems should normally derive
    the user identity from authentication/JWT/session
    rather than trusting a client-provided header.
    """

    user_id = request.headers.get("X-User-ID")

    if user_id:
        return f"user:{user_id}"

    # Anonymous users can fall back to IP
    return f"anonymous:{get_remote_address(request)}"


user_limiter = Limiter(
    key_func=get_user_identifier,
    headers_enabled=True,
)


@app.get("/user-limit")
@user_limiter.limit("10/minute")
async def user_limit(request: Request):

    """
    Rate limit is based on USER.

    User A:

        X-User-ID: user_1

        10 requests/minute


    User B:

        X-User-ID: user_2

        10 requests/minute


    They have independent buckets.
    """

    return {
        "message": "User-level rate limiting",
    }


# ============================================================
# API KEY RATE LIMITING
# ============================================================

def get_api_key(request: Request) -> str:
    """
    Rate limit based on API key.

    Example:

        X-API-Key: abc123

    Useful for:

        Public APIs
        ML inference APIs
        Developer APIs
        SaaS platforms
    """

    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return f"anonymous:{get_remote_address(request)}"

    return f"api_key:{api_key}"


api_key_limiter = Limiter(
    key_func=get_api_key,
    headers_enabled=True,
)

@app.get("/api/inference")
@api_key_limiter.limit("20/minute")
async def inference(request: Request, response:Response):

    """
    Example AI inference endpoint.

    20 requests/minute per API key.
    """

    return {
        "message": "Inference executed"
    }
