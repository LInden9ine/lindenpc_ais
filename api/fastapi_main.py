# api/fastapi_main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import router  # Абсолютный импорт

load_dotenv()

app = FastAPI()

# CORS middleware (for allowing requests from your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router)

# Optionally, you can add a root endpoint for testing purposes


@app.get("/")
async def read_root():
    return {"message": "FastAPI backend is running"}

if __name__ == "__main__":
    # This block is only executed when the script is run directly,
    # not when it's imported as a module.
    import uvicorn

    # Get the port from the environment variable, default to 8000 if not set
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
