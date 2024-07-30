from datetime import datetime,timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import joinedload

# Imports from Configurations:
from src.Configuration import settings
from src.Configuration.settings import get_settings
from src.Configuration.security import generate_token, get_token_payload, str_decode, str_encode, unique_string, get_current_user
# Imports from Models:
from src.Models.TokenModel import Token



# ========================================================================================================================
settings = get_settings()

# ### Purpose: Generate a JWT token for the user ###
# async def _generate_tokens(user, session):
#     # 1) Generate refresh and access keys
#     refresh_key = unique_string(100)
#     access_key = unique_string(50)

#     # 2) Compute expiration times
#     rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
#     at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

#     # 3) Initialize an instance of Token
#     user_token = Token()
#     user_token.user_id = user.id
#     user_token.refresh_key = refresh_key
#     user_token.access_key = access_key
#     user_token.expires_at = datetime.now(timezone.utc) + rt_expires

#     # 4) Store token in the database
#     session.add(user_token)
#     session.commit()
#     session.refresh(user_token)

#     # 5) Construct payload dictionary for the JWT access token
#     at_payload = {
#         "sub": str_encode(str(user.id)),
#         "a": access_key,
#         "r": str_encode(str(user_token.id)),
#         "n": str_encode(f"{user.username}"),
#         "role": str_encode(user.role)
#     }

#     # 6) Generate access token
#     access_token = generate_token(at_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, at_expires)

#     # 7) Construct payload dictionary for the Refresh JWT token
#     rt_payload = {"sub": str_encode(str(user.id)),
#                   "t": refresh_key,
#                   "a": access_key,
#     }
#     # 8) Generate the refresh token:
#     refresh_token = generate_token(rt_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM, rt_expires)

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "expires_in": at_expires.seconds
#     }





# ### Purpose: Generate a new access and refresh token for the user:
# async def get_refresh_token(refresh_token, session):
#     # 1) Assess the JWT token's payload:
#     token_payload = get_token_payload(refresh_token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
#     if not token_payload:
#         raise HTTPException(status_code=400, detail="Invalid Request.")

#     # 2) Retrieve information from the payload:
#     refresh_key = token_payload.get('t')
#     access_key = token_payload.get('a')
#     user_id = str_decode(token_payload.get('sub'))


#     # 3) Retrieve the token from the db and ensure it matches the refresh and access keys, user id, and has not expired
#     user_token = session.query(Token).options(joinedload(Token.user)).filter(
#         Token.refresh_key == refresh_key,
#         Token.access_key == access_key,
#         Token.user_id == user_id,
#         Token.expires_at > datetime.now(timezone.utc)).first()

#     if not user_token:
#         raise HTTPException(status_code=400, detail="Invalid Request.")

#     # 4) Set the expiry of the old refresh token to the current time => Invalidate the token:
#     user_token.expires_at = datetime.now(timezone.utc)
#     session.add(user_token)
#     session.commit()

#     # 5) Generate a new access and refresh token for the user
#     return await _generate_tokens(user_token.user, session)





async def _generate_tokens(user, session):
    refresh_key = unique_string(100)
    access_key = unique_string(50)

    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    user_token = Token()
    user_token.user_id = user.id
    user_token.refresh_key = refresh_key
    user_token.access_key = access_key
    user_token.expires_at = datetime.now(timezone.utc) + rt_expires

    session.add(user_token)
    session.commit()
    session.refresh(user_token)

    at_payload = {
        "sub": str_encode(str(user.id)),
        "a": access_key,
        "r": str_encode(str(user_token.id)),
        "n": str_encode(f"{user.username}"),
        "role": str_encode(user.role)
    }

    access_token = generate_token(at_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, at_expires)

    rt_payload = {"sub": str_encode(str(user.id)), "t": refresh_key, "a": access_key}
    refresh_token = generate_token(rt_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM, rt_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": at_expires.seconds
    }

async def get_refresh_token(refresh_token, session):
    token_payload = get_token_payload(refresh_token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
    if not token_payload:
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token.")

    refresh_key = token_payload.get('t')
    access_key = token_payload.get('a')
    user_id = str_decode(token_payload.get('sub'))

    user_token = session.query(Token).options(joinedload(Token.user)).filter(
        Token.refresh_key == refresh_key,
        Token.access_key == access_key,
        Token.user_id == user_id,
        Token.expires_at > datetime.now(timezone.utc)).first()

    if not user_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token request.")

    user_token.expires_at = datetime.now(timezone.utc)
    session.commit()

    return await _generate_tokens(user_token.user, session)