import json
import os
import base64
from pathlib import Path
from typing import Optional

import openai
import requests
from pdfminer.high_level import extract_text as pdf_extract_text
from PIL import Image
import pytesseract

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

CONFIG_PATH = Path("config.json")
UPLOAD_DIR = Path("uploads")
FIKEN_BASE_URL = "https://api.fiken.no/api/v2"

app = FastAPI(title="Accounting Genie")
app.mount("/static", StaticFiles(directory="frontend"), name="static")


def load_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r") as f:
            return json.load(f)
    return {
        "fikenClientId": "",
        "fikenClientSecret": "",
        "fikenCompanySlug": "",
        "fikenAccessToken": "",
        "fikenRefreshToken": "",
        "openaiKey": "",
    }


def save_config(cfg: dict):
    with CONFIG_PATH.open("w") as f:
        json.dump(cfg, f)


def extract_text_from_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return pdf_extract_text(str(path))
    return pytesseract.image_to_string(Image.open(path))


def parse_invoice(text: str, openai_key: str) -> dict:
    if not openai_key:
        raise RuntimeError("OpenAI key not configured")
    openai.api_key = openai_key
    prompt = (
        "Extract invoice details as JSON with keys: invoice_number, date, due_date, "
        "supplier, total_amount, currency."
    )
    messages = [
        {"role": "system", "content": "You extract fields from invoices."},
        {"role": "user", "content": prompt + "\n\n" + text},
    ]
    resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    content = resp.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw": content}


def post_invoice_to_fiken(data: dict, cfg: dict) -> dict:
    if not cfg.get("fikenAccessToken") or not cfg.get("fikenCompanySlug"):
        raise RuntimeError("Fiken access not configured")
    headers = {
        "Authorization": f"Bearer {cfg['fikenAccessToken']}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    url = f"{FIKEN_BASE_URL}/companies/{cfg['fikenCompanySlug']}/inbox"
    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    return res.json()


@app.get("/")
def index():
    return FileResponse("frontend/index.html")


@app.get("/api/config")
def get_config():
    cfg = load_config()
    return cfg


@app.post("/api/config")
async def set_config(cfg: dict):
    save_config(cfg)
    return {"status": "saved"}


@app.get("/api/redirect-url")
def get_redirect_url(request: Request):
    url = str(request.url_for("fiken_callback"))
    return {"redirectUrl": url}


@app.get("/api/callback")
def fiken_callback(code: Optional[str] = None):
    # TODO: Exchange code for tokens and store them
    return {"received_code": code}


@app.post("/api/upload")
async def upload_receipt(file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(exist_ok=True)
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        f.write(await file.read())
    cfg = load_config()
    text = extract_text_from_file(dest)
    invoice = parse_invoice(text, cfg.get("openaiKey"))
    try:
        fiken_resp = post_invoice_to_fiken(invoice, cfg)
        status = "posted"
    except Exception as e:
        fiken_resp = str(e)
        status = "parsed"
    return {
        "status": status,
        "filename": file.filename,
        "invoice": invoice,
        "fikenResponse": fiken_resp,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
