from fastapi import FastAPI
from app.db.database import engine, Base
from app.routes import user_routes, auth_routes, column_routes, board_routes, task_routes
from fastapi.middleware.cors import CORSMiddleware
from app.routes import projects_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kanban Management API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(board_routes.router, prefix="/boards", tags=["Boards"])
app.include_router(column_routes.router, prefix="/columns", tags=["Columns"])
app.include_router(projects_routes.router, prefix="/projects", tags=["Projects"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])
