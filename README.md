# AI-Powered Accounting Genie

This project aims to create a simple prototype for uploading receipt images or PDF files and eventually sending them to Fiken. The prototype exposes a small FastAPI server with a minimal user interface.

## Features (Prototype)
- Basic configuration UI for storing Fiken API keys and an OpenAI API key.
- Endpoint to generate the redirect URL used in the Fiken OAuth setup.
- Placeholder endpoint for uploading receipt files.
- Windows `run.bat` script for launching the server quickly.

## Running
1. Install the dependencies (FastAPI and Uvicorn). In many Python environments these are available already, but you can install them with:
   ```bash
   pip install fastapi uvicorn
   ```
2. Double-click `run.bat` (on Windows) or run the equivalent command on other platforms:
   ```bash
   python -m uvicorn main:app --reload
   ```
3. Open `http://localhost:8000/` in your browser. Use the form to enter your Fiken `client_id`, `client_secret`, and OpenAI API key. The page also displays the redirect URL you must register in the Fiken developer settings.

The current implementation only saves the configuration locally and accepts uploads. Actual calls to Fiken or OpenAI are left as TODOs.

## Firestore Schema
See `docs/firestore_schema.md` for an outline of the planned Firestore collections.
