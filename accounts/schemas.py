from pydantic import BaseModel
from typing import Optional
class SignupModel(BaseModel):
    username : str
    email : str
    password : str
    
    class Config:
        orm_mode=True
        

class LoginModel(BaseModel):
    username : str
    password : str
    