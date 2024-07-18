# from src.Responses.base import BaseResponse
from pydantic import BaseModel


class LoginResponse(BaseModel):
  access_token: str
  refresh_token: str
  expires_in: int
  token_type: str = "Bearer"