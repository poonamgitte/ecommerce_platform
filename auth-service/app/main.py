"""
Entry point of Auth Microservice
"""

from fastapi import FastAPI
from app.routes import auth

app = FastAPI(
    title="Auth Service",
    description="Authentication microservice for ecommerce platform",
    version="1.0.0"
)

# Register routes
app.include_router(auth.router)


# Health check
@app.get("/")
async def health_check():
    return {"message": "Auth Service Running"}