from fastapi import FastAPI, HTTPException, APIRouter
from typing import List
from db import database, users
from models import UserIn, UserOut
from security import generate_salt, hash_password
import base64

app = FastAPI()

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut)
async def register_user(user: UserIn):

    existing_user = await database.fetch_one(
        users.select().where(users.c.email == user.email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # 1. Crear salt
    salt = generate_salt()
    salt_b64 = base64.b64encode(salt).decode()

    # 2. Crear hash (verifier)
    verifier = hash_password(user.password, salt)

    # 3. Guardar usuario
    query = users.insert().values(
        email=user.email,
        username=user.username,
        phonenumber=user.phonenumber,
        salt=salt_b64,
        verifier=verifier
    )

    user_id = await database.execute(query)

    return UserOut(
        id=user_id,
        email=user.email,
        username=user.username,
        phonenumber=user.phonenumber
    )

@router.post("/login")
async def login_user(user: UserIn):
    """
    Login seguro usando salt + hash almacenado.
    """

    # 1. Buscar el usuario
    db_user = await database.fetch_one(
        users.select().where(users.c.email == user.email)
    )
    if not db_user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    # 2. Recuperar salt y verifier
    salt = base64.b64decode(db_user["salt"])
    stored_verifier = db_user["verifier"]

    # 3. Hashear la contraseña ingresada por el usuario
    calculated_hash = hash_password(user.password, salt)

    # 4. Comparar
    if calculated_hash != stored_verifier:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {
        "message": "Login exitoso",
        "email": db_user["email"],
        "username": db_user["username"]
    }
