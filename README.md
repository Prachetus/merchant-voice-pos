# Merchant Voice POS

Voice-first merchant inventory platform with a Flask API, MongoDB storage, and a Next.js frontend.

## What this app is built for

- Natural language inventory commands like `add 2.5 kg rice` or `remove 3 packets milk`.
- Merchant-friendly item matching for kg, gram, liter, packet, bottle, box, and similar quantities.
- Authenticated workflows for login, registration, dashboard access, and voice event logging.
- Optional LLM-based parsing using any OpenAI-compatible, freely available provider.

## Architecture

- Backend: Flask + Flask-JWT-Extended + MongoDB.
- Frontend: Next.js App Router.
- Voice parsing: local parser first, LLM fallback when `LLM_BASE_URL` and `LLM_API_KEY` are set.

## Repository layout

- `app.py`: Flask API entrypoint.
- `database.py`: MongoDB connection, index creation, and seed helpers.
- `frontend/`: Next.js app with landing page, auth screens, and dashboard shell.

## Environment

Copy the example files:

- `.env.example` for the Flask backend.
- `frontend/.env.example` for the Next.js frontend.

## Backend routes

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/inventory`
- `POST /api/inventory`
- `PATCH /api/inventory/<id>`
- `DELETE /api/inventory/<id>`
- `POST /api/voice/parse`
- `POST /api/voice/commit`

## Local development

1. Start MongoDB and set `MONGODB_URI`.
2. Start the Flask API with `python app.py`; it ensures indexes and seeds default inventory on startup.
3. In `frontend/`, install dependencies and run `npm run dev`.

## Production deployment

The repository now includes container entrypoints for a production-style deployment.

1. Build and run the full stack with `docker compose up --build`.
2. The backend runs under Gunicorn in the API container.
3. The frontend runs as a built Next.js app in its own container.
4. MongoDB is provided as a dedicated service with persisted data.

Required production settings:

- `JWT_SECRET_KEY`
- `MONGODB_URI`
- `CORS_ORIGINS`
- `LLM_BASE_URL` and `LLM_API_KEY` when using a hosted LLM parser

## Codespaces

- Open port `3000` for the frontend.
- API requests are proxied through Next.js, so you do not need to forward `5000` for the browser.
- The included `.devcontainer/devcontainer.json` auto-opens the frontend port.

## LLM support

The backend accepts an OpenAI-compatible chat endpoint through:

- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

When configured, the API uses the LLM to interpret free-form merchant speech for items, quantities, and units. When it is not configured, the local parser still handles common stock commands.
