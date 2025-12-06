from pydantic import BaseModel, EmailStr, constr
from typing import Literal

class UserIn(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)  
    usertype: Literal['consumer', 'professional']
    password: constr(min_length=8)  
    token: str
    
class UserLogin(BaseModel): 
    email: EmailStr
    password: constr(min_length=8)
    
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
