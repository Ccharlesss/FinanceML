# from datetime import datetime
# from typing import List, Union
# from pydantic import EmailStr
# from src.Responses.UserResponse import UserResponse
# from src.Responses.base import BaseResponse


# class RoleResponse(BaseResponse):
#     role_name: str
#     users: List[UserResponse]



from typing import List
from pydantic import BaseModel
from src.Responses.UserResponse import UserResponse


class RoleResponse(BaseModel):
    role_name: str
    users: List[UserResponse]