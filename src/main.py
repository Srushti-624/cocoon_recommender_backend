from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import settings
from src.database.mongo import connect_to_mongo, close_mongo_connection
from src.routes import auth_routes, farmer_routes, admin_routes, recommendation_routes, health_routes
from src.services.ml_service import ml_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    ml_service.load_model()  # Load ML model on startup
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Cocoon Rearing Recommender API",
    description="ML-based recommendation system for silk farmers",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(farmer_routes.router)
app.include_router(admin_routes.router)
app.include_router(recommendation_routes.router)
app.include_router(health_routes.router)

@app.get("/")
async def root():
    return {
        "message": "Cocoon Rearing Recommender API",
        "version": "1.0.0",
        "status": "running"
    }
