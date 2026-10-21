from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from app.routers.branches import router as branches_router
from app.routers.rooms import router as rooms_router
from app.routers.employees import router as employees_router
from app.routers.auth import router as auth
from app.routers.roles import router as roles_router
from app.routers.employee_roles import router as employee_roles_router
from app.routers.teacher_profile import router as teacher_profile_router
from app.routers.lead_sources import router as lead_sources_router
from app.routers.lead_statuses import router as lead_statuses_router
from app.routers.courses import router as courses_router
from app.routers.students import router as students_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.rate_limiting import limiter_by_user_id



app = FastAPI(title="ERP system api" , version="1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#         "http://localhost:5500",
#         "http://127.0.0.1:5500",
#         "http://localhost:8000",
#         "http://127.0.0.1:8000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.state.limiter = limiter_by_user_id
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth)
app.include_router(roles_router)
app.include_router(employee_roles_router)
app.include_router(branches_router)
app.include_router(rooms_router)
app.include_router(employees_router)
app.include_router(teacher_profile_router)
app.include_router(lead_sources_router)
app.include_router(lead_statuses_router)
app.include_router(courses_router)
app.include_router(students_router)
add_pagination(app)
# app.mount("/static", StaticFiles(directory="static"), name="static")
#
#
# @app.get("/", include_in_schema=False)
# async def index():
#     return FileResponse("static/index.html")
