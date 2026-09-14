from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_routes ,space_routes ,project_routes ,material_routes ,quiz_routes ,tutor_routes ,analytics_routes,home_routes,admin_routes

app = FastAPI(title="AI Study Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(space_routes.router, prefix="/spaces", tags=["Spaces"])
app.include_router(project_routes.router, prefix="/projects", tags=["Projects"])
app.include_router(material_routes.router, prefix="/materials", tags=["Materials"])
app.include_router(quiz_routes.router, prefix="/quiz", tags=["Quiz"])
app.include_router(tutor_routes.router, prefix="/tutor", tags=["Tutor"])
app.include_router(analytics_routes.router, prefix="/analytics", tags=["Analytics"])
app.include_router(home_routes.router, prefix="/home", tags=["Home"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
@app.get("/")
def health_check():
    return {"status": "ok"}