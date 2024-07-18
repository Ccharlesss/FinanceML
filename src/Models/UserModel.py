from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from src.Configuration.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    # Define the table name in the db for the Model:
    __tablename__ = "Users"
    # id: PK of type Int:
    id = Column(Integer, primary_key=True, autoincrement=True)
    # username: of type Str must be unique:
    username = Column(String(100), unique=True)
    # email of type Str must be unique:
    email = Column(String(100), unique=True, index=True)
    # password of type Str:
    password = Column(String(100))
    # is_authenticated status of type Bool:
    is_authenticated = Column(Boolean, default=False)
    # is_active status of type Bool:
    is_active = Column(Boolean, default=False)
    # created_at of type Datetime:
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    # updated_at of type Datetime:
    updated_at = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    # role title: of type String
    role = Column(String(20), nullable=True)


    # Define relationship with Tokenc Model: 1:*
    tokens = relationship("Token", back_populates="user")


    def get_context_string(self, context: str) -> str:
        if self.updated_at:
            return f"{context}{self.password[-6:]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".strip()
        return context
