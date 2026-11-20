
import os
import requests

from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")


def verify_firebase_token(id_token: str):

    if not FIREBASE_WEB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Firebase API key is not configured"
        )

    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:lookup?key={FIREBASE_WEB_API_KEY}"
    )

    try:
        response = requests.post(
            url,
            json={"idToken": id_token},
            timeout=15
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Firebase verification is unavailable"
        )

    result = response.json()

    if response.status_code != 200:
        error_message = result.get("error", {}).get("message", "")

        if error_message.startswith("USER_DISABLED"):
            raise HTTPException(
                status_code=403,
                detail="This Firebase account is disabled"
            )

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Firebase token"
        )

    users = result.get("users", [])

    if len(users) != 1:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase account"
        )

    user = users[0]

    if user.get("disabled") is True:
        raise HTTPException(
            status_code=403,
            detail="This Firebase account is disabled"
        )

    uid = user.get("localId")
    phone = user.get("phoneNumber")

    if not uid or not phone:
        raise HTTPException(
            status_code=401,
            detail="Verified phone account is required"
        )

    return {
        "uid": uid,
        "phone": phone
    }
