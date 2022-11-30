from pydantic import BaseModel


class UserSch(BaseModel):
    username: str

