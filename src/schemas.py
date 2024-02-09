from pydantic import BaseModel


class Course(BaseModel):
    direction: str
    value: str

    class Config:
        orm_mode = True


class Exchange(BaseModel):
    exchanger: str
    courses: list[Course]

    class Config:
        orm_mode = True