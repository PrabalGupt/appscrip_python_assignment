from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.routes_analyze import router as analyze_router
from app.config import settings
from app.core.security import authenticate_user, create_access_token
from app.schemas.auth import Token

app = FastAPI(
    title="Trade Opportunities API",
    version="1.0.0",
    description="Analyzes Indian sectors and returns markdown trade opportunity reports.",
)

# mount routers
app.include_router(analyze_router, prefix="")

# health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
