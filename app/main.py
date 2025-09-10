from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chats import chatRoutes

app = FastAPI(
    title="Apple Store Backend API",
    description="Backend API for Apple Store application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatRoutes.router)

@app.get("/")
async def root():
    return {"message": "Apple Store Backend API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)