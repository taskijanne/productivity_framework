"""
FastAPI application for the AI Productivity Framework.

This application provides REST API endpoints to access productivity metrics
stored in the SQLite database.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router


# Create FastAPI application
app = FastAPI(
    title="AI Productivity Framework API",
    description="API for accessing productivity metrics and observations",
    version="1.0.0"
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
