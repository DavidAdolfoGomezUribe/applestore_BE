from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chatRoutes, userRoutes, productRoutes

app = FastAPI(
    title="Apple Store Backend API",
    description="Backend API for Apple Store application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routers
app.include_router(chatRoutes.router)
app.include_router(userRoutes.router)
app.include_router(productRoutes.router)

@app.get("/")
async def root():
    return {"message": "Apple Store Backend API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)