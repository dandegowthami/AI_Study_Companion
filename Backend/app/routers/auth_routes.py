from fastapi import APIRouter, HTTPException
from uuid import uuid4
from datetime import datetime

from app.database import users_col
from app.schemas import SignupRequest, LoginRequest, AuthResponse
from app.auth import hash_password, verify_password, create_token

router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
def signup(data: SignupRequest):
    if users_col.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid4())
    users_col.insert_one({
        "_id": user_id,
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "role": "user",
        "created_at": datetime.utcnow(),
    })

    token = create_token(user_id, "user")
    return AuthResponse(token=token, user_id=user_id, name=data.name, role="user")


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    user = users_col.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["_id"], user["role"])
    return AuthResponse(token=token, user_id=user["_id"], name=user["name"], role=user["role"])