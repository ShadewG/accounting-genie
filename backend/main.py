import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import RedirectResponse
import firebase_admin
from firebase_admin import credentials, firestore, storage
from . import fiken, ocr

app = FastAPI()

if not firebase_admin._apps:
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET")
        })
    else:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set")

_db = firestore.client()
_bucket = storage.bucket()


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/api/fiken/login")
def fiken_login():
    return RedirectResponse(fiken.get_auth_url())


@app.get("/api/fiken/callback")
async def fiken_callback(code: str):
    tokens = await fiken.exchange_code(code)
    # In a real app, store tokens linked to the authenticated user
    return tokens


@app.post("/api/receipts")
async def upload_receipt(file: UploadFile = File(...), user_id: str = Form(...)):
    receipt_id = str(uuid.uuid4())
    blob = _bucket.blob(f"receipts/{receipt_id}/{file.filename}")
    blob.upload_from_file(file.file)
    blob.make_public()
    doc = {
        "userId": user_id,
        "filePath": blob.public_url,
        "status": "pending_ocr",
    }
    _db.collection("receipts").document(receipt_id).set(doc)
    ocr.extract_and_update(receipt_id, doc["filePath"])
    return {"receipt_id": receipt_id}


@app.post("/api/receipts/{receipt_id}/post_to_fiken")
async def post_to_fiken(receipt_id: str, access_token: str = Form(...)):
    doc_ref = _db.collection("receipts").document(receipt_id)
    snap = doc_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Receipt not found")
    expense = ocr.prepare_fiken_expense(snap.to_dict())
    await fiken.create_expense(expense, access_token)
    doc_ref.update({"status": "posted_to_fiken"})
    return {"status": "posted"}
