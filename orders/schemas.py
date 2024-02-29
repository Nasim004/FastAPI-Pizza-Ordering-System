from pydantic import BaseModel
from typing import Optional

class OrderModal(BaseModel):
    quantity : int
    pizza_size : str
    order_status : Optional[str] = None
    user_id : Optional[int] = None
    
    
    class Config:
        orm_mode = True
        schema_extra={
            "example":{
                "quantity":2,
                "pizza_size":"SMALL"
            }
        }
        
class OrderStatusModel(BaseModel):
    order_status:Optional[str]="pending"
    

