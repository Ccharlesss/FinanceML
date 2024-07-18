# from pydantic import BaseModel, ConfigDict

# class BaseResponse(BaseModel):
#   model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


from pydantic import BaseModel


class BaseResponse(BaseModel):
    class Config:
        # This configuration allows arbitrary types and converts attributes to fields
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        # By default, extra fields are not allowed
        extra = "forbid"