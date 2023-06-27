from pydantic import BaseModel


def _snake_to_camel_case(string: str) -> str:
    words = string.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class RealWorldBaseModel(BaseModel):
    class Config:
        orm_mode = True
        alias_generator = _snake_to_camel_case
        validate_assignment = True
