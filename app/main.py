from fastapi import FastAPI
from app.routers.branches import router as branches_router
from app.routers.rooms import router as rooms_router
from app.routers.employees import router as employees_router
from app.routers.auth import router as auth
from app.routers.roles import router as roles_router

app = FastAPI(title="ERP system api" , version="1.0")
app.include_router(auth)
app.include_router(roles_router)
app.include_router(branches_router)
app.include_router(rooms_router)
app.include_router(employees_router)
