from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes import user_routes, auth_routes
from fastapi.middleware.cors import CORSMiddleware
from app.routes import project_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kanban Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(project_routes.router, prefix="/projects", tags=["Projects"])