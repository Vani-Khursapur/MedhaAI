
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.routers.auth import get_verified_user
from app.schemas.ai import AISearchRequest
from app.services.ai_service import (
    begin_ai_operation,
    generate_ai_result,
    finish_ai_operation,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


# --------------------------------------------------
# Common response helper
# --------------------------------------------------

def ai_response(status_code: int, data: dict):
    return JSONResponse(
        status_code=status_code,
        content=data,
        headers={"Cache-Control": "no-store"}
    )


# --------------------------------------------------
# Database error handling
# --------------------------------------------------

def format_ai_database_error(data: dict):
    message = (
        data.get("message")
        or data.get("error")
        or ""
    )

    if isinstance(message, dict):
        message = message.get("message", "")

    if not isinstance(message, str):
        message = ""

    if "Request limit reached" in message or "Credit limit reached" in message:
        return ai_response(403, {
            "success": False,
            "code": "allowance_exhausted",
            "message": "This plan has no included searches remaining this month."
        })

    if message == "AI request ID conflict":
        return ai_response(400, {
            "success": False,
            "code": "request_conflict",
            "message": "This request ID belongs to a different AI operation."
        })

    if message == "Chapter text is not indexed for this workspace":
        return ai_response(503, {
            "success": False,
            "code": "chapter_not_indexed",
            "message": (
                "This chapter has not been indexed for your selected workspace. "
                "Ask your institute owner to connect its documents."
            )
        })

    access_errors = {
        "Access denied",
        "Owner not found or inactive",
        "Active institute membership required",
        "Active paid subscription required",
        "Account is disabled",
        "Active user required",
        "Active registered user required",
        "Use the subscription provider key",
        "Provider key needs attention",
        "AI operation ownership mismatch"
    }

    if message in access_errors:
        return ai_response(403, {
            "success": False,
            "message": (
                "Your selected plan, account or provider key needs attention. "
                "Refresh access or contact the institute owner."
            )
        })

    if "Invalid AI request" in message:
        return ai_response(400, {
            "success": False,
            "message": "Check the AI request and try again."
        })

    return ai_response(503, {
        "success": False,
        "message": (
            "AI service setup or storage is temporarily unavailable. "
            "Please try again later."
        )
    })


# --------------------------------------------------
# Provider error response formatting
# --------------------------------------------------

def format_ai_provider_error(data: dict, outcome: dict):

    if (
        data.get("statusCode") != 422
        or not isinstance(data.get("response"), dict)
        or data["response"].get("code") != "ai_failed"
        or outcome.get("state") != "failed"
    ):
        return data

    messages = {
        "provider_auth": (
            "The AI provider key was rejected. Contact the plan owner "
            "or administrator. Your search allowance was restored."
        ),
        "provider_permissions": (
            "The AI provider key cannot access this service. Contact "
            "the plan owner or administrator. Your search allowance was restored."
        ),
        "provider_billing": (
            "The AI provider account needs billing or balance attention. "
            "Contact the plan owner or administrator. Your search allowance was restored."
        ),
        "provider_model": (
            "The configured AI model is unavailable for this provider account. "
            "Contact the administrator. Your search allowance was restored."
        ),
        "provider_request": (
            "The AI service rejected this request. Contact the administrator. "
            "Your search allowance was restored."
        ),
        "output_incomplete": (
            "The AI response stopped before it finished. Your search allowance "
            "was restored. Please retry."
        ),
        "content_blocked": (
            "The AI provider could not process this selection. Try a different "
            "crop or prompt. Your search allowance was restored."
        ),
        "invalid_result": (
            "The AI response could not be read. Your search allowance was "
            "restored. Please retry."
        )
    }

    failure = outcome.get("failure")

    if failure not in messages:
        return data

    return {
        **data,
        "response": {
            "success": False,
            "code": f"ai_{failure}",
            "message": messages[failure]
        }
    }


# --------------------------------------------------
# AI Search endpoint
# --------------------------------------------------

@router.post("/search")
async def ai_search(
    request: AISearchRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_verified_user)
):

    # Step 1: Reserve the AI operation in PostgreSQL

    try:
        print("DEBUG: Starting AI reservation")

        reservation = begin_ai_operation(
            db,
            user["uid"],
            request
        )

        print("DEBUG: AI reservation completed")

        # Handle cached results or operations that do not need generation
        if not reservation.get("execute"):

            if reservation.get("statusCode") and reservation.get("response"):
                return ai_response(
                    reservation["statusCode"],
                    reservation["response"]
                )

            return format_ai_database_error(reservation)

    except Exception as exc:
        db.rollback()

        print(
            "DEBUG: AI reservation failed:",
            type(exc).__name__,
            repr(exc)
        )

        return ai_response(503, {
            "success": False,
            "message": (
                "AI service setup or storage is temporarily unavailable. "
                "Please try again later."
            )
        })

    # Step 2: Generate the AI response

    try:
        print("DEBUG: Starting AI generation")

        outcome = await generate_ai_result(
            request,
            reservation
        )

        print("DEBUG: AI generation completed")

    except Exception as exc:
        print(
            "DEBUG: AI generation failed:",
            type(exc).__name__,
            repr(exc)
        )

        # Do not automatically retry a provider request whose outcome is unknown.
        outcome = {
            "state": "uncertain"
        }

    # Step 3: Finalize the operation in PostgreSQL

    try:
        print("DEBUG: Starting AI finalization")

        finalized = finish_ai_operation(
            db,
            user["uid"],
            str(request.requestId),
            str(reservation["lease"]),
            outcome
        )

        print("DEBUG: AI finalization completed")

        if not isinstance(finalized, dict):
            return ai_response(503, {
                "success": False,
                "message": (
                    "Unable to finalize the AI operation. "
                    "Please try again later."
                )
            })

        # Handle database errors returned by finalization
        if (
            not isinstance(finalized.get("statusCode"), int)
            or not isinstance(finalized.get("response"), dict)
        ):
            return format_ai_database_error(finalized)

        # Format provider-specific failure messages
        formatted = format_ai_provider_error(
            finalized,
            outcome
        )

        return ai_response(
            formatted["statusCode"],
            formatted["response"]
        )

    except Exception as exc:
        db.rollback()

        print(
            "DEBUG: AI finalization failed:",
            type(exc).__name__,
            repr(exc)
        )

        return ai_response(503, {
            "success": False,
            "message": (
                "Unable to finalize the AI operation. "
                "Please try again later."
            )
        })
