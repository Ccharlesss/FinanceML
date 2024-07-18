from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func, ForeignKey
from src.Configuration.database import Base
from sqlalchemy.orm import relationship

class Token(Base):
    # Define the table name in db that stores Token Model:
    __tablename__ = "Tokens"
    # id: PK of type integer:
    id = Column(Integer, primary_key=True, autoincrement=True)
    # access_key of type Str:
    access_key = Column(String(250), nullable=True, index=True, default=None)
    # refresh_key of type Str:
    refresh_key = Column(String(250), nullable=True, index=True, default=None)
    # creation time of type Datetime:
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    # expiration time of type Datetime:
    expires_at = Column(DateTime, nullable=False)

    # user_id: FK of type Int
    user_id = Column(Integer, ForeignKey('Users.id'))
    # Define relationship with User: 1:* => User has many tokens and a token belongs to a specific user
    user = relationship("User", back_populates="tokens")
