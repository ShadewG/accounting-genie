# AI-Powered Accounting Genie

This project aims to create a simple prototype for uploading receipt images or PDF files and eventually sending them to Fiken. The prototype exposes a small FastAPI server with a minimal user interface. It now includes simple AI powered invoice extraction and posts the parsed data to the Fiken API.

## Features (Prototype)
- Basic configuration UI for storing Fiken API keys and an OpenAI API key.
- Endpoint to generate the redirect URL used in the Fiken OAuth setup.
- Endpoint for uploading invoice files which are parsed with OpenAI and then sent to Fiken.
- Windows `run.bat` script for launching the server quickly.

## Running
1. Install the dependencies. In many Python environments FastAPI and Uvicorn are available already. The project also requires the OpenAI client, pdfminer, pytesseract and Pillow:
   ```bash
   pip install -r requirements.txt
   ```
2. Double-click `run.bat` (on Windows) or run the equivalent command on other platforms:
   ```bash
   python -m uvicorn main:app --reload
   ```
3. Open `http://localhost:8000/` in your browser. Use the form to enter your Fiken `client_id`, `client_secret`, and OpenAI API key. The page also displays the redirect URL you must register in the Fiken developer settings.

Uploaded invoices will be parsed with OpenAI and the extracted fields will be submitted to your Fiken account.

## Firestore Schema
See `docs/firestore_schema.md` for an outline of the planned Firestore collections.
