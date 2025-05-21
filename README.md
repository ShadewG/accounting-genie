# AI-Powered Accounting Genie

This prototype demonstrates a minimal workflow for uploading receipts,
processing them with AI, and creating Fiken expenses. It is **not** a
finished product but shows the basic pieces required.

## Features
- Upload receipt images which are stored in Firebase Storage
- Placeholder OCR/AI extraction using OpenAI
- OAuth2 flow for obtaining Fiken access tokens
- Endpoint to create an expense in Fiken

## Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide a Firebase service account JSON and set the environment variable
   `GOOGLE_APPLICATION_CREDENTIALS` to its path. Also set
   `FIREBASE_STORAGE_BUCKET` with your Firebase Storage bucket name.
3. Set Fiken credentials and redirect URL via environment variables:
   `FIKEN_CLIENT_ID`, `FIKEN_CLIENT_SECRET`, `FIKEN_REDIRECT_URI`, and
   `FIKEN_COMPANY` (company slug).
4. Optionally, set `OPENAI_API_KEY` for AI extraction.

## Running
Use the `run.bat` script on Windows or run Uvicorn manually:
```bash
python -m uvicorn backend.main:app --reload
```
The server exposes endpoints under `http://localhost:8000`.

## Status
This repository only contains a thin demo. Functions such as OCR parsing,
OpenAI integration, and Fiken API calls are simplified. Further development
is required before it can be used in production.
