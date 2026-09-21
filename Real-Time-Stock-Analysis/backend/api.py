from fastapi import FastAPI

from backend.routes import router


app = FastAPI(
    title="Real-Time Stock Analysis API",
    description="Backend API for the Real-Time Stock Analysis and Prediction Dashboard",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Stock Analysis API is running"
    }


app.include_router(router)