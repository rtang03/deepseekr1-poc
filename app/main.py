from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
import json
import logging
from pydantic_settings import BaseSettings
from functools import lru_cache
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("uvicorn")


# https://medium.com/@ramanbazhanau/preparing-fastapi-for-production-a-comprehensive-guide-d167e693aa2b


# Application settings
class Settings(BaseSettings):
    app_name: str = "MyFastAPI App"
    admin_email: str = "None"
    database_url: str = "None"
    secret_key: str = "None"
    allowed_hosts: list = ["*", "localhost"]
    debug: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


# end of application settings

app = FastAPI()

# Configure CORS in FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# end of CORS configuration

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )


# end of rate limiting


# Host validation
@app.middleware("http")
async def validate_host(request, call_next):
    settings = get_settings()
    host = request.headers.get("host", "").split(":")[0]
    if settings.debug or host in settings.allowed_hosts:
        return await call_next(request)
    logger.error(f"Host {host} not allowed")
    raise HTTPException(status_code=400, detail="Invalid host")


# end of host validation


@app.get("/info")
async def info():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "debug_mode": settings.debug,
    }


@app.get("/health")
async def health_check():
    # Perform checks (e.g., database connection, external services)
    all_systems_operational = True
    if all_systems_operational:
        return JSONResponse(content={"status": "healthy"}, status_code=200)
    else:
        return JSONResponse(content={"status": "unhealthy"}, status_code=503)


@app.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy(request: Request, path: str, scheme: str = "http"):
    url = f"{scheme}://localhost:11434/{path}"

    async def stream_response(response):
        async for chunk in response.aiter_bytes():
            yield chunk

    try:
        async with httpx.AsyncClient() as client:
            response = None
            if request.method == "GET":
                response = await client.get(
                    url, headers=request.headers, params=request.query_params
                )
                if response:
                    return HTMLResponse(response.text, status_code=200)
                else:
                    return HTMLResponse(content="No response", status_code=500)
            elif request.method == "POST":
                content = await request.json()
                # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    # examples of api calls
                    # /api/generate
                    # json={"model": "deepseek-r1:1.5B", "prompt": "Why is the sky blue?"}
                    # /api/chat
                    # json={"model": "deepseek-r1:1.5B","messages": [{"role":"user","content":"Why is the sky blue?","stream":false}]}
                    json=content,
                    # https://www.python-httpx.org/advanced/timeouts/
                    timeout=60.0,
                )

                if response:
                    return HTMLResponse(response.text, status_code=200)
                    # Note: StreamingResponse is not working as expected
                    # return StreamingResponse(
                    #     stream_response(response), status_code=response.status_code
                    # )
                else:
                    return HTMLResponse(content="No response", status_code=500)
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
        )
        return HTMLResponse(
            content=f"HTTP error occurred: {exc.response.status_code}",
            status_code=exc.response.status_code,
        )
    except httpx.TimeoutException or httpx.ReadTimeout as exc:
        logger.error(f"Request timed out: {exc}")
        return HTMLResponse(content="Request timed out", status_code=408)
    except Exception as exc:
        logger.error(f"An unknown error occurred: {type(exc)}")
        return HTMLResponse(content="An internal error occurred", status_code=500)


def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
