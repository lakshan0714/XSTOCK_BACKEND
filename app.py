from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.routes.user_routes import user_router
from src.config.database import Base,  sync_engine
from src.config.settings import Settings
import logging
from contextlib import asynccontextmanager
from src.utils.init_super_admin import create_super_admin
from src.config.database import SessionLocal

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db = SessionLocal()
    try:
        create_super_admin(db)
    finally:
        db.close()
    yield 


settings=Settings()



app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for cse stock Project",
    version="1.0.0",
    lifespan=lifespan )

# Create tables synchronously
Base.metadata.create_all(bind=sync_engine)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix="/user", tags=["user"])

# Run app
if __name__ == "__main__":
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)