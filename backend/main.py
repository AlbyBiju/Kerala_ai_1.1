from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api.auth import router as auth_router
from app.api.shipments import router as shipments_router
from app.api.dashboard import router as dashboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    await init_db()
    yield

app = FastAPI(
    title="ExportGuard API",
    description="Automated Export Document Verification System API",
    version="0.1.0",
    lifespan=lifespan
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(shipments_router)
app.include_router(dashboard_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "ExportGuard Verification API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
