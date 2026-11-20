from fastapi import FastAPI
from app.routers.institute import router as institute_router
from app.routers.auth import router as auth_router
from app.routers.billing import router as billing_router
from app.routers.admin import router as admin_router
from app.routers.ai import router as ai_router
from app.routers.usage import router as usage_router

app = FastAPI(
    title="Medha AI API",
    description="Backend APIs for Medha AI",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Medha AI Backend is running!"
    }

app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(admin_router)
app.include_router(institute_router)
app.include_router(ai_router)
app.include_router(usage_router)