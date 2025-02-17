from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
import httpx
import uvicorn
import logging
import json

app = FastAPI()

# Configure Uvicorn logging
# https://github.com/fastapi/fastapi/issues/1508
uvicorn_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


@app.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy(request: Request, path: str, scheme: str = "http"):
    logger = logging.getLogger("uvicorn.access")

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
                    return HTMLResponse(
                        content=response.text, status_code=response.status_code
                    )
                else:
                    return HTMLResponse(content="No response", status_code=500)
            elif request.method == "POST":
                content = await request.json()
                logger.info(f"Request content: {json.dumps(content)}")
                # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    # /api/generate
                    # json={"model": "deepseek-r1:1.5B", "prompt": "Why is the sky blue?"}
                    # /api/chat
                    # json={"model": "deepseek-r1:1.5B","messages": [{"role":"user","content":"Why is the sky blue?","stream":false}]}
                    json=content,
                )

                if response:
                    return StreamingResponse(
                        stream_response(response), status_code=response.status_code
                    )
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
    except Exception as exc:
        logger.error(f"An error occurred: {exc}")
        return HTMLResponse(content="An internal error occurred", status_code=500)


def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        log_config=uvicorn_log_config,
    )


if __name__ == "__main__":
    main()
