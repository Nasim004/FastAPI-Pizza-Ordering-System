import logging
from .models import Orders
from fastapi import APIRouter
from accounts.models import User
from fastapi import Depends,status
from database import engine,Session
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from .schemas import OrderModal,OrderStatusModel
from sqlalchemy.exc import SQLAlchemyError,ProgrammingError
from accounts.utils import get_token_from_header,authorize_token

db=Session(bind=engine)
logger = logging.getLogger(__name__)
order_router = APIRouter(prefix='/orders')
logging.basicConfig(level=logging.INFO,  
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
                    datefmt='%Y-%m-%d %H:%M:%S',  
                    filename='app.log',  
                    filemode='a')  



@order_router.get("/")
async def hello():
    return {"Message":"Hello Welcome"}


@order_router.post("/neworder")
def new_order(order:OrderModal,token:str = Depends(get_token_from_header)):
    """
    Create a new order with the provided quantity and pizza size.
    Requires a valid token for authentication and authorization.
    """
    try:
        subject = authorize_token(token)
        if subject:
            user = db.query(User).filter(User.username == subject).first()
            new_order = Orders(
                quantity=order.quantity,
                pizza_size=order.pizza_size,
                user=user
            )
            db.add(new_order)
            db.commit()
            return JSONResponse(content="New Order Placed", status_code=status.HTTP_201_CREATED)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@order_router.patch("/update/status/{order_id}")
def order_status_update(order_id: int, order: OrderStatusModel, token: str = Depends(get_token_from_header)):
    """
    Updates the status of an order.

    Args:
        order_id (int): The ID of the order to be updated.
        order (OrderStatusModel): The model representing the updated order status.
        token (str): The token obtained from the Authorization header.

    Returns:
        dict: A dictionary containing the success message or error message.

    Raises:
        HTTPException: If the token is missing, has an invalid format, or the user is not an admin.
    """
    try:
        subject = authorize_token(token)
        current_user = db.query(User).filter(User.username == subject).first()
        if current_user.is_staff:
            current_order = db.query(Orders).filter(Orders.id == order_id).first()
            current_order.order_status = order.order_status
            try:
                db.commit()
                return {"content": f"Order {order_id} status updated to {order.order_status}"}
            except SQLAlchemyError as e:
                logger.error("Database error", exc_info=True)
                db.rollback()
                raise HTTPException(detail="Database error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error("User is not admin", exc_info=True)
            return JSONResponse (content="User is not admin", status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error("An unexpected error occurred", exc_info=True)
        raise HTTPException(detail=str(e), status_code=status.HTTP_401_UNAUTHORIZED)
    
    
@order_router.get("/allorders")
def get_all_order( token: str = Depends(get_token_from_header)):
    """
    Retrieves all orders from the database if the user is an admin.
    Requires a valid token in the Authorization header to authenticate the user.
    If the user is not an admin, returns an unauthorized response.
    """
    try:
        subject = authorize_token(token)
        current_user = db.query(User).filter(User.username == subject).first()
        if current_user.is_staff:
            orders = db.query(Orders).all()
            return jsonable_encoder(orders)
        return JSONResponse(content="User is not admin", status_code=status.HTTP_401_UNAUTHORIZED)
    except :
        raise HTTPException(detail="Invalid Token", status_code=status.HTTP_401_UNAUTHORIZED)
    
@order_router.get("/myorders")
def get_my_orders( token: str = Depends(get_token_from_header)):
    """
    Get an order by ID.

    Parameters:
    - id (int): The ID of the order to retrieve.

    Returns:
    - dict: The JSON representation of the order.

    Raises:
    - HTTPException: If there is an error retrieving the order from the database or if the token is invalid or unauthorized.
    """
    try:
        subject = authorize_token(token)
        current_user = db.query(User).filter(User.username == subject).first() 
        return jsonable_encoder(current_user.orders)
    except :
        raise HTTPException(detail="Invalid Token", status_code=status.HTTP_401_UNAUTHORIZED)


@order_router.delete('/deleteorder/{id}')
def delete_order(id: int, token: str = Depends(get_token_from_header)):
    """
    Deletes an order from the database.

    Parameters:
    - id (int): The ID of the order to be deleted.
    - token (str): The authorization token obtained from the Authorization header.

    Returns:
    - JSONResponse: A JSON response indicating the success of the deletion operation.

    Raises:
    - HTTPException: If the user is not authorized to delete the order or if the token is invalid.
    """
    try:
        subject = authorize_token(token)
        user = db.query(User).filter(User.username == subject).first()
        order = db.query(Orders).filter(Orders.id == id).first()
        if user.is_staff or order.user_id == user.id : 
            
            db.delete(order)
            return JSONResponse (content=f"Order {id} deleted", status_code=status.HTTP_200_OK)
        raise HTTPException(detail="Not Authorized", status_code=status.HTTP_401_UNAUTHORIZED )
    except :
        raise HTTPException(detail="Invalid Token", status_code=status.HTTP_401_UNAUTHORIZED)
    