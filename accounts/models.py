from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer,String,Boolean,Text
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer,primary_key=True)
    username = Column(String(25),unique=True)
    email = Column(String(50),unique=True)
    password = Column(Text,nullable=True)
    is_staff = Column(Boolean,default=False)
    is_active = Column(Boolean, default=True)
    orders = relationship("Orders", back_populates="user")
   

    
    def __repr__(self):
        return f"<User {self.username}"
    