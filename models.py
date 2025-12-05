from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    email: EmailStr
    username: str
    phonenumber: str | None = None
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    phonenumber: str | None = None
