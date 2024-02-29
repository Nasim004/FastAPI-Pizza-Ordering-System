from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy import Column, Integer, ForeignKey,String
class Orders(Base):
    
    
    

    
    __tablename__ = 'orders'
    id = Column(Integer,primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(String,default="Pending")
    pizza_size = Column(String,nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User",back_populates="orders")
    
    def __repr__(self):
        return f"<order {self.id}"