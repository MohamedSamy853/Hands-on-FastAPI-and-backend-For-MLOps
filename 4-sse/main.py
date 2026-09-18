from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import time


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=['*'],
    allow_credentials=True,
    allow_origins=["*"]
)


# ============================================================
# Request Model
# ============================================================

class PromptRequest(BaseModel):
    text: str


# ============================================================
# 1. Simple SSE-style Streaming
# ============================================================

def generate_text(text: str):
    """
    Simple generator to demonstrate streaming.

    Instead of returning the whole response at once,
    we yield small chunks progressively.
    """

    for character in text:
        yield f"data: {character}\n\n"
        time.sleep(0.2)
        


@app.post("/stream/text")
def stream_text(request: PromptRequest):

    return StreamingResponse(
        generate_text(request.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# 2. Streaming LLM using Ollama
# ============================================================

# Ollama OpenAI-compatible API
ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="no_key"
)


def generate_ollama(prompt: str):

    response = ollama_client.chat.completions.create(
        model="qwen3:4b ",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=True,
    )

    for chunk in response:

        content = chunk.choices[0].delta.content

        if content:
            yield f"data: {content}\n\n"

    # SSE convention: end of stream
    yield "data: [DONE]\n\n"


@app.post("/stream/ollama")
async def stream_ollama(request: PromptRequest):

    return StreamingResponse(
        generate_ollama(request.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# 3. Streaming LLM using vLLM
# ============================================================

# vLLM OpenAI-compatible API
vllm_client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)


def generate_vllm(prompt: str):

    response = vllm_client.chat.completions.create(
        model="qwen3:7b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=True,
    )

    for chunk in response:

        content = chunk.choices[0].delta.content

        if content:
            
            yield f"data: {content}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/stream/vllm")
def stream_vllm(request: PromptRequest):

    return StreamingResponse(
        generate_vllm(request.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )