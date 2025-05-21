import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

CONFIG_PATH = Path('config.json')
UPLOAD_DIR = Path('uploads')

app = FastAPI(title="Accounting Genie")
app.mount("/static", StaticFiles(directory="frontend"), name="static")


def load_config():
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open('r') as f:
            return json.load(f)
    return {"fikenClientId": "", "fikenClientSecret": "", "openaiKey": ""}


def save_config(cfg: dict):
    with CONFIG_PATH.open('w') as f:
        json.dump(cfg, f)


@app.get("/")
def index():
    return FileResponse('frontend/index.html')


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
    url = str(request.url_for('fiken_callback'))
    return {"redirectUrl": url}


@app.get("/api/callback")
def fiken_callback(code: Optional[str] = None):
    # TODO: Exchange code for tokens and store them
    return {"received_code": code}


@app.post("/api/upload")
async def upload_receipt(file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(exist_ok=True)
    dest = UPLOAD_DIR / file.filename
    with dest.open('wb') as f:
        f.write(await file.read())

    # TODO: Send image/PDF to OpenAI for analysis and post to Fiken
    return {"status": "uploaded", "filename": file.filename}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
