from pydantic import BaseModel
from pydantic.utils import to_lower_camel


class RealWorldBaseModel(BaseModel):
    class Config:
        orm_mode = True
        alias_generator = to_lower_camel
        validate_assignment = True
        allow_population_by_field_name = True
