import os
from jose import jwt
from typing import Optional
from fastapi import status,Header
from datetime import datetime,timedelta
from dotenv import load_dotenv,find_dotenv
from fastapi.exceptions import HTTPException

load_dotenv(find_dotenv())

ACCESS_TOKEN_EXPIRES_TIME = 30
REFRESH_TOKEN_EXPIRES_TIME = 60 * 24 * 7
ALGORITHM = "HS256"
ACCESS_SECRET_KEY = os.getenv('access_token_secret_key')
REFRESH_SECRET_KEY = os.getenv('refresh_token_secret_key')


def create_access_token(subject: str) -> str:
    """
    Generate a JSON Web Token (JWT) access token with an expiration time.

    Args:
        subject (str): The subject of the access token.

    Returns:
        str: The generated access token as a JWT.
    """
    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_TIME)
    to_encode = {"exp": expire_time, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str) -> str:
    """
    Generate a JSON Web Token (JWT) for refreshing authentication tokens.

    Args:
        subject: The subject of the token.

    Returns:
        The generated refresh token.

    """
    expire_time = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_TIME)
    to_encode = {"exp": expire_time, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token:str) -> str:
    """
    Decode the access token using a secret key and algorithm.

    Args:
        token (str): The access token to be decoded.

    Returns:
        str: The value of the 'sub' claim from the decoded token.
    """
    try:
        decoded_jwt = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=ALGORITHM)
        return decoded_jwt['sub']
    except:
        raise HTTPException(detail="Invalid Token",status_code=status.HTTP_401_UNAUTHORIZED)

def decode_refresh_token(token:str) -> str:
    """
    Decode the refresh token using a secret key and algorithm.

    Args:
        token (str): The refresh token to be decoded.

    Returns:
        str: The value of the 'sub' claim from the decoded token.
    """
    try:
        decoded_jwt = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=ALGORITHM)
        return decoded_jwt['sub']
    except:
        raise HTTPException(detail="Invalid Token",status_code=status.HTTP_401_UNAUTHORIZED)
    
async def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Get the token from the Authorization header.

    Parameters:
    - authorization (Optional[str]): The Authorization header value. Defaults to None.

    Returns:
    - str: The extracted token.

    Raises:
    - HTTPException: If the Authorization header is missing, has an invalid format, or uses an invalid authentication scheme.
    """
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header format")
    
def authorize_token(token:str) -> str:
    """
    Authorizes a token by decoding it using a secret key and algorithm.

    Args:
        token (str): The token to be authorized.

    Returns:
        str: The subject of the token obtained after decoding and authorization.

    Raises:
        HTTPException: If any exception occurs during the decoding or authorization process.
            The exception has the detail message "Invalid token" and the status code 401 Unauthorized.
    """
    try:
        subject = decode_access_token(token)
        return subject
    except Exception:
        raise HTTPException(detail="Invalid access token", status_code=status.HTTP_401_UNAUTHORIZED)
    