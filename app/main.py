from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import userRoutes
# from app.routes import chatRoutes, productRoutes

app = FastAPI(
    title="Apple Store Backend API",
    description="Backend API for Apple Store application with JWT authentication",
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
# app.include_router(productRoutes.router)
# app.include_router(chatRoutes.router)
app.include_router(userRoutes.router)

@app.get("/")
async def root():
    return {"message": "Apple Store Backend API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)