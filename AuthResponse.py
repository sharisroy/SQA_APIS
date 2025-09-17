from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request model
class AuthRequest(BaseModel):
    username: str
    password: str

# Response model
class AuthResponse(BaseModel):
    success: bool
    token: str | None = None
    error: str | None = None

@app.post("/login", response_model=AuthResponse)
async def login(payload: AuthRequest):
    if payload.username == "admin" and payload.password == "1234":
        return AuthResponse(success=True, token="fake-jwt-token")
    return AuthResponse(success=False, error="Invalid credentials")
