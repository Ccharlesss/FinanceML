# from datetime import datetime
# from typing import Union
# from pydantic import EmailStr
# from src.Responses.base import BaseResponse


# class UserResponse(BaseResponse):
#     id: int
#     username: str
#     email: EmailStr
#     role: str
#     is_active: bool
#     is_authenticated: bool
#     created_at: Union[str, None, datetime] = None



# class AccountCreatedResponse(BaseResponse):
#     id: int
#     username: str
#     email: EmailStr
#     role: str
#     is_active: bool
#     is_authenticated: bool
#     created_at: Union[str, None, datetime] = None





from datetime import datetime
from typing import Union
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    is_authenticated: bool
    created_at: Union[str, None, datetime] = None




class AccountCreatedResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    is_authenticated: bool
    created_at: Union[str, None, datetime] = None
