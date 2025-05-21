import os
import httpx

FIKEN_BASE = "https://api.fiken.no"
CLIENT_ID = os.environ.get("FIKEN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("FIKEN_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("FIKEN_REDIRECT_URI")
COMPANY_SLUG = os.environ.get("FIKEN_COMPANY")


def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "fiken:write",
    }
    return f"{FIKEN_BASE}/oauth/authorize?" + httpx.QueryParams(params).encode()


async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FIKEN_BASE}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def create_expense(data: dict, access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{FIKEN_BASE}/api/v2/companies/{COMPANY_SLUG}/expenses",
            json=data,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()
