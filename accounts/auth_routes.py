from .models import User
from database import Session,engine
from .utils import get_token_from_header
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from .schemas import SignupModel, LoginModel
from fastapi import APIRouter,HTTPException,status,Depends
from werkzeug.security import generate_password_hash,check_password_hash
from .utils import create_access_token, create_refresh_token, decode_refresh_token,authorize_token

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
db = Session(bind=engine)

@auth_router.get("/")
async def home(token: str = Depends(get_token_from_header)):
    try:
        subject = authorize_token(token)
        print("**"*20,subject)
        if subject:
            return {"hello"}
    except Exception as e :
        raise e
        # raise HTTPException(detail="Invalid access token",status_code=status.HTTP_401_UNAUTHORIZED)
    
    
@auth_router.post("/signup")
async def signup(user: SignupModel) -> JSONResponse:
    """
    Endpoint for user signup.
    Checks if the user already exists in the database based on their email or username.
    If the user does not exist, a new user is created and added to the database.

    Args:
        user (SignupModel): The user's username, email, and password.

    Returns:
        JSON response indicating that the user has been created.
    """
    # Check if a user with the same email or username already exists
    db_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if db_user :
        if db_user.email == user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with email already exists")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with username already exists")   
    # Create a new User object with the provided username, email, and hashed password
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    # Add the new user to the db and commit the changes to the database

    try:
    # perform some operations
        db.add(new_user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise
    finally:
        db.close()
    return JSONResponse(content=f"User Created",status_code=status.HTTP_201_CREATED)
        
@auth_router.post("/login")
async def login(user: LoginModel) -> JSONResponse:
    """
    Handles the login functionality by checking the provided username and password against the database.
    If the credentials are valid, it generates an access token and a refresh token, and returns them in the response.
    If the credentials are invalid, it raises an HTTPException with a 401 status code.

    :param user: A model representing the user's login credentials, including the username and password.
    :return: JSON response containing the access token and refresh token if login is successful.
             Raises an HTTPException with a 401 status code and an error message if login fails.
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_token = create_access_token(user.username)
        refresh_token = create_refresh_token(user.username)
        response = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return JSONResponse(content=response, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        
@auth_router.post("/refreshtoken")
async def refresh_token(token: str = Depends(get_token_from_header)) -> JSONResponse:
    try:
        subject = decode_refresh_token(token)
    except Exception:
        raise HTTPException(detail="Invalid refresh token", status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token = create_access_token(subject)
    response = {
        "access_token": access_token
    }
    return JSONResponse(content=response, status_code=status.HTTP_200_OK)
