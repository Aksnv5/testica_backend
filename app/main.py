import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, test, result, test_run
from core.database import engine, Base
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(test.router)
app.include_router(test_run.router)
# app.include_router(result.router)


# create tables helper (for dev). In prod use Alembic migrations.
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVER_PORT, reload=True)
