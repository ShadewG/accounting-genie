import json
import openai
from firebase_admin import firestore

openai.api_key = openai.api_key or ''

db = firestore.client()

def extract_and_update(receipt_id: str, file_url: str):
    """Placeholder OCR and AI extraction."""
    raw_text = "Sample OCR text"  # Replace with call to OCR service
    doc_ref = db.collection("receipts").document(receipt_id)
    doc_ref.update({"rawText": raw_text})

    prompt = (
        "Extract vendor, date and total amount from this receipt text. "
        "Respond in JSON with fields vendor, date, totalAmount.\n\n" + raw_text
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        extracted = json.loads(resp.choices[0].message["content"])
    except Exception:
        extracted = {}

    doc_ref.update({"extractedData": extracted, "status": "pending_review"})
    return extracted


def prepare_fiken_expense(receipt_data: dict) -> dict:
    data = receipt_data.get("extractedData", {})
    return {
        "date": data.get("date"),
        "amount": data.get("totalAmount"),
        "description": data.get("vendor"),
        "vatType": "HIGH",
        "account": 6300,
        "vatIncluded": True,
        "supplierName": data.get("vendor"),
    }
