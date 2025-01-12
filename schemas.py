from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    username: str = None
    password: str

class UserRead(BaseModel):
    email: str
    username: str = None
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MoodLogCreate(BaseModel):
    user_id: int
    mood: str