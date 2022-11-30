from pydantic import BaseModel


class UserSch(BaseModel):
    username: str
    email: str
    password: str

