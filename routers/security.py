# from datetime import datetime, timedelta
# from jose import jwt
# from passlib.context import CryptContext
# from typing import Optional
# from database.crud import get_user_by_username

# # Security settings
# SECRET_KEY = "your-secret-key-here"  # Change this in production
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password: str, hashed_password: str):
#     return pwd_context.verify(plain_password, hashed_password)



# # def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
# #     to_encode = data.copy()
# #     if expires_delta:
# #         expire = datetime.utcnow() + expires_delta
# #     else:
# #         expire = datetime.utcnow() + timedelta(minutes=15)
# #     to_encode.update({"exp": expire})
# #     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# #     return encoded_jwt

# # def authenticate_user(db, username: str, password: str):
# #     user = get_user_by_username(db, username)
# #     if not user:
# #         return False
# #     if not verify_password(password, user.hashed_password):
# #         return False
# #     return user