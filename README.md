# Backend Development with FastAPI — for AI, ML & MLOps Engineers

A practical, code-heavy session by **MLOps MENA Community** on the backend skills an AI/ML engineer needs to take a model from a notebook to a production service — built around **FastAPI**, with a full integration example using **vLLM**.

This repo/session does **not** aim to turn you into a full-stack backend engineer. The goal is to give you exactly enough backend depth to confidently build, serve, and productionize AI systems.

## What You'll Be Able to Do

- Understand HTTP & API fundamentals and design clean endpoints
- Validate AI/ML inputs and outputs with Pydantic
- Structure a FastAPI project that scales past a single notebook script
- Use PostgreSQL through SQLAlchemy, with Alembic migrations
- Apply dependency injection for models, databases, and config
- Reason correctly about async, concurrency, and I/O- vs CPU-bound work
- Implement rate limiting and middleware for expensive endpoints
- Handle authentication, authorization, and errors safely
- Stream responses with WebSockets and Server-Sent Events
- Integrate a FastAPI service with a vLLM inference server
- Dockerize and configure a production-style AI service
- Recognize and avoid common backend mistakes AI engineers make

## Topics Covered

### 1. Why Backend, and Why FastAPI?
The gap between a trained model and a production AI service. What FastAPI is (built on Starlette + ASGI, powered by Pydantic), why it fits AI workloads, and a quick comparison with Flask and Django REST Framework.

### 2. What Is an API?
Client/server, request/response, and the key mental model: **an API endpoint is just a remote function call** — `POST /predict` ≈ `predict(features)`.

### 3. HTTP Request Anatomy
Method, URL, path, query parameters, headers, and body — what each one is for, with FastAPI examples for each (path params, query params, request body with Pydantic, headers).

### 4. HTTP Methods & Status Codes
GET / POST / PUT / PATCH / DELETE, idempotency, and why inference is `POST /predict` and not `GET /predict`. Status codes relevant to AI services (200, 201, 202, 204, 400, 401, 403, 404, 409, 422, 429, 500, 503).

### 5. Pydantic & Validation
Field constraints, nested models, and why validation must happen **before** inference — invalid requests should never reach your model, GPU, or token budget.

### 6. Response Models & Serialization
Using `response_model` as a data contract to control exactly what leaves your API and avoid leaking internal fields.

### 7. Project Structure
A clean layout for an AI service (`api/`, `schemas/`, `services/`, `repositories/`, `core/`, `dependencies/`, `db/`) instead of everything in `main.py`.

### 8. SQLAlchemy ORM
Models, sessions, and CRUD operations against PostgreSQL, plus a note on Alembic for migrations.

### 9. Dependency Injection
Using `Depends()` for database sessions, loaded models, and config — and why this matters for testing.

### 10. Concurrency & Async
`def` vs `async def`, where async wins (I/O-bound work: DB calls, HTTP requests, calling LLM providers), and the critical warning: **async does not make CPU-heavy ML inference faster**. Offloading blocking work with thread pools.

### 11. Rate Limiting
Why AI APIs need it (inference is expensive), common strategies (fixed window, sliding window, token bucket, leaky bucket), and a Redis-backed example.

### 12. Middleware
Cross-cutting logic — logging, timing, CORS, security headers — and when to prefer `Depends()` instead.

### 13. Authentication vs Authorization
"Who are you?" vs "What are you allowed to do?" with a JWT-based example.

### 14. Error Handling
`HTTPException`, custom exception handlers, and the difference between 4xx (client) and 5xx (server) errors — including what should never be exposed to a client.

### 15. WebSockets
Persistent, bidirectional connections for real-time chat, live inference, and streaming agent responses.

### 16. Server-Sent Events (SSE)
One-way streaming, and why it's often the simpler choice for token-by-token LLM output.

### 17. FastAPI + vLLM
Why you wouldn't call vLLM directly from the client: authentication, rate limiting, validation, conversation management, and business logic all live in the FastAPI layer in front of it. Includes a full example calling vLLM's OpenAI-compatible API, plus a streaming version.

### 18. Production Project: Todo API
An end-to-end example service (FastAPI + PostgreSQL + SQLAlchemy + Alembic + Pydantic + Docker) with full CRUD endpoints, proper schemas, dependency injection, and a Dockerfile + docker-compose.yml — and how it evolves into an AI service (FastAPI → AI Service → PostgreSQL → Redis → vLLM).

### 19. Production Considerations
Config & secrets, health checks, logging, metrics (Prometheus/Grafana), scaling, and resilience (timeouts, retries, graceful shutdown, connection pooling).

### 20. Common FastAPI Mistakes
The recurring mistakes AI engineers make — and the fix for each — including blocking calls in async endpoints, reloading models per request, missing validation, missing rate limits, and hardcoded secrets.

## Tech Stack

`FastAPI` · `Pydantic` · `SQLAlchemy` · `Alembic` · `SQL`  `vLLM` · `Docker` / `Docker Compose`

## About

Session by **MLOps MENA Community** — a community for MLOps, AI, and ML engineers across the MENA region.
