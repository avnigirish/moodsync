from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = None

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MoodLogCreate(BaseModel):
    user_id: int
    mood: str