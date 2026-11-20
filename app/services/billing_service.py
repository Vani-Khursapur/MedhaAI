from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException
import requests


def create_billing_order(
    db: Session,
    firebase_uid: str,
    request_id,
    offering: str,
    ai_mode: str,
    billing: str,
    seats: int,
    institute_name: str | None,
    name: str,
    email: str,
    credential_id
):
    try:
        result = db.execute(
        text("""
            SELECT public.api_create_billing_order(
                CAST(:uid AS text),
                CAST(:request_id AS uuid),
                CAST(:offering AS text),
                CAST(:ai_mode AS text),
                CAST(:billing AS text),
                CAST(:seats AS integer),
                CAST(:institute_name AS text),
                CAST(:name AS text),
                CAST(:email AS text),
                CAST(:credential_id AS uuid)
            )
        """),
        {
            "uid": firebase_uid,
            "request_id": request_id,
            "offering": offering,
            "ai_mode": ai_mode,
            "billing": billing,
            "seats": seats,
            "institute_name": institute_name,
            "name": name,
            "email": email,
            "credential_id": credential_id
        }
    )

        response = result.scalar_one()
        db.commit()

        return response

    except DBAPIError as error:
        db.rollback()

        original_error = getattr(error, "orig", None)
        print("Billing database error:", str(original_error or error))
        message = str(original_error) if original_error else str(error)
        sqlstate = (
            getattr(original_error, "sqlstate", None)
            or getattr(original_error, "pgcode", None)
        )

        if "Request ID already used for a different subscription" in message:
            raise HTTPException(
                status_code=409,
                detail="This requestId was already used for different billing details."
            )

        if "Verify an API key for this account and offering first" in message:
            raise HTTPException(
                status_code=403,
                detail="Verify your API key for this account and plan first."
            )

        if "Account is disabled" in message:
            raise HTTPException(
                status_code=403,
                detail="This account is disabled."
            )

        if sqlstate == "22023":
            raise HTTPException(
                status_code=400,
                detail="Invalid billing request. Check your subscription details."
            )

        if sqlstate == "42501":
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to create this billing order."
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to create billing order."
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while creating billing order."
        )


def verify_provider_key(
    db: Session,
    firebase_uid: str,
    offering: str,
    provider: str,
    api_key: str
):
    try:
        # 1. Check registered user and encryption configuration
        result = db.execute(
            text("""
                SELECT
                    (public.medha_user_from_uid(
                        CAST(:uid AS text)
                    )).id AS user_id,

                    EXISTS (
                        SELECT 1
                        FROM medha_private.byok_keyring
                        WHERE singleton = TRUE
                          AND secret IS NOT NULL
                    ) AS encryption_ready
            """),
            {"uid": firebase_uid}
        )

        account = result.mappings().one()

        if not account["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="An active registered account is required to verify a provider key."
            )

        if not account["encryption_ready"]:
            raise HTTPException(
                status_code=503,
                detail="API key encryption is not configured. Ask the administrator to run the BYOK SQL patch."
            )

        # 2. Prepare provider verification request
        if provider == "openai":
            url = "https://api.openai.com/v1/models"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            params = None

        else:
            url = "https://generativelanguage.googleapis.com/v1beta/models"
            headers = {
                "x-goog-api-key": api_key
            }
            params = {"pageSize": 1}

        # 3. Verify the key with the provider
        try:
            provider_response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=15,
                allow_redirects=False
            )

        except requests.RequestException:
            raise HTTPException(
                status_code=503,
                detail="The provider could not verify this key right now. Please try again."
            )

        status = provider_response.status_code

        if status in (400, 401, 403):
            raise HTTPException(
                status_code=400,
                detail="The provider rejected this key. Check its permissions and try again."
            )

        if status == 429:
            raise HTTPException(
                status_code=429,
                detail="The provider is rate limiting verification. Please try again later."
            )

        if status != 200:
            raise HTTPException(
                status_code=503,
                detail="The provider could not verify this key right now. Please try again."
            )

        # 4. Check whether accessible models were returned
        try:
            data = provider_response.json()
        except ValueError:
            raise HTTPException(
                status_code=503,
                detail="The provider could not verify this key right now. Please try again."
            )

        models = (
            data.get("data")
            if provider == "openai"
            else data.get("models")
        )

        if not isinstance(models, list) or not models:
            raise HTTPException(
                status_code=400,
                detail="No accessible models were returned for this key. Check its model-list permissions."
            )

        # 5. Encrypt and store the verified key
        result = db.execute(
            text("""
                SELECT public.medha_store_verified_key_pgcrypto(
                    CAST(:uid AS text),
                    CAST(:offering AS text),
                    CAST(:provider AS text),
                    CAST(:api_key AS text)
                )
            """),
            {
                "uid": firebase_uid,
                "offering": offering,
                "provider": provider,
                "api_key": api_key
            }
        )

        response = result.scalar_one()

        if not response or not response.get("success"):
            raise HTTPException(
                status_code=500,
                detail="Your verified key could not be saved. Please try again."
            )

        db.commit()

        return {
            "success": True,
            "verified": True,
            "credentialId": str(response["credentialId"]),
            "provider": response["provider"]
        }

    except HTTPException:
        db.rollback()
        raise

    except DBAPIError as error:
        db.rollback()

        original_error = getattr(error, "orig", None)
        message = str(original_error or error)

        if any(term in message for term in (
            "Account is disabled",
            "Active registered user required",
            "Active user required"
        )):
            raise HTTPException(
                status_code=403,
                detail="An active registered account is required to verify a provider key."
            )

        if any(term in message for term in (
            "medha_private",
            "byok_keyring",
            "medha_store_verified_key_pgcrypto",
            "BYOK encryption is not configured"
        )):
            raise HTTPException(
                status_code=503,
                detail="API key encryption is not configured. Ask the administrator to run the BYOK SQL patch."
            )

        if "Invalid provider credential" in message:
            raise HTTPException(
                status_code=400,
                detail="Enter a valid provider API key without spaces."
            )

        raise HTTPException(
            status_code=500,
            detail="Your verified key could not be saved. Please try again."
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Your verified key could not be saved. Please try again."
        )
