from pydantic import BaseModel

class ProfileCreate(BaseModel):
    name: str
    skill: str
    years_of_experience: int

class ProfileOut(BaseModel):
    id: int
    name: str
    skill: str
    years_of_experience: int

    class Config:
        orm_mode = True
