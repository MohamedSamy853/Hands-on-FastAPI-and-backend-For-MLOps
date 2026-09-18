from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import asyncio


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=['*'],
    allow_credentials=True,
    allow_origins=["*"]
)


# ============================================================
# Clients
# ============================================================

# Ollama OpenAI-compatible API
ollama_client = AsyncOpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
)


# vLLM OpenAI-compatible API
vllm_client = AsyncOpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="EMPTY",
)

#"pip install 'uvicorn[standard]'", or install 'websockets' or 'wsproto' manually.
# ============================================================
# 1. Simple WebSocket Streaming
# ============================================================

@app.websocket("/ws/text")
async def websocket_text(websocket: WebSocket):

    # Accept WebSocket connection
    await websocket.accept()

    try:

        while True:

            # Receive message from browser
            text = await websocket.receive_text()

            # Stream the text character by character
            for character in text:

                await websocket.send_text(character)

                # Only for demonstration
                # to make streaming visible
                await asyncio.sleep(0.05)

            # Tell the client that
            # the response is finished
            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:

        print("Client disconnected")


# ============================================================
# 2. Ollama WebSocket Streaming
# ============================================================

@app.websocket("/ws/ollama")
async def websocket_ollama(websocket: WebSocket):

    # Accept WebSocket connection
    await websocket.accept()

    try:

        while True:

            # Receive prompt from browser
            prompt = await websocket.receive_text()

            # Ask Ollama for a streaming response
            stream = await ollama_client.chat.completions.create(
                model="qwen3:4b",

                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],

                stream=True,
            )

            # Forward every generated chunk
            # to the WebSocket client
            async for chunk in stream:

                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:

                    await websocket.send_text(content)

            # Tell the client that
            # generation is finished
            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:

        print("Client disconnected")


# ============================================================
# 3. vLLM WebSocket Streaming
# ============================================================

@app.websocket("/ws/vllm")
async def websocket_vllm(websocket: WebSocket):

    # Accept WebSocket connection
    await websocket.accept()

    try:

        while True:

            # Receive prompt from browser
            prompt = await websocket.receive_text()

            # Ask vLLM for a streaming response
            stream = vllm_client.chat.completions.create(
                model="YOUR_MODEL_NAME",

                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],

                stream=True,
            )

            # Forward every generated chunk
            # to the WebSocket client
            for chunk in stream:

                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:

                    await websocket.send_text(content)

            # Tell the client that
            # generation is finished
            await websocket.send_text("[DONE]")

    except WebSocketDisconnect:

        print("Client disconnected")