from fastapi import FastAPI, HTTPException, APIRouter
from typing import List
from db import database, users
from models import UserIn, UserOut, UserLogin
from security import generate_salt, hash_password
import base64
import bleach
import os
import httpx

app = FastAPI()

router = APIRouter(prefix="/users", tags=["users"])

RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")

@router.post("/register", response_model=UserOut)
async def register_user(user: UserIn):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": RECAPTCHA_SECRET, "response": user.token}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        result = response.json()
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="No se pudo verificar reCAPTCHA. Intenta de nuevo.")

    
    clean_username = bleach.clean(user.username)  
    user.username = clean_username

    existing_user = await database.fetch_one(
        users.select().where(users.c.email == user.email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    salt = generate_salt()
    salt_b64 = base64.b64encode(salt).decode()
    verifier = hash_password(user.password, salt)

    query = users.insert().values(
        email=user.email,
        username=user.username,
        usertype=user.usertype,
        salt=salt_b64,
        verifier=verifier
    )

    user_id = await database.execute(query)

    return UserOut(
        id=user_id,
        email=user.email,
        username=user.username
    )

@router.post("/login")
async def login_user(user: UserLogin):
    """
    Login seguro usando salt + hash almacenado.
    """

    db_user = await database.fetch_one(
        users.select().where(users.c.email == user.email)
    )
    if not db_user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    salt = base64.b64decode(db_user["salt"])
    stored_verifier = db_user["verifier"]

    calculated_hash = hash_password(user.password, salt)

    if calculated_hash != stored_verifier:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {
        "message": "Login exitoso",
        "email": db_user["email"],
        "username": db_user["username"]
    }
