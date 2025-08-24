import http
import time

from fastapi import Request, Response

from app.logger import logger


async def log_request_middleware(request: Request, call_next):
    """
    Logs every request with processing time and status.
    Example:
        127.0.0.1:52144 - "GET /ping" 200 OK  1.23 ms
    """
    url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
    host = getattr(getattr(request, "client", None), "host", "-")

    start = time.perf_counter()

    try:
        response: Response = await call_next(request)
    except Exception:
        # Log *and* re-raise so FastAPI default handlers still run
        logger.exception(
            f'{host} - "{request.method} {url}" 500 Internal Server Error', extra={"hide_src": True}
        )  # supress filename:lineno
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000
    status_phrase = http.HTTPStatus(response.status_code).phrase

    logger.info(
        f'{host} - "{request.method} {url}" ' f"{response.status_code} {status_phrase} {elapsed_ms:.2f} ms",
        extra={"hide_src": True},
    )  # supress filename:lineno
    return response
