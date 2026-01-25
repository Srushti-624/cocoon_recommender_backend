from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.models.user_model import UserRegister, UserLogin, UserResponse, TokenResponse
from src.database.mongo import get_users_collection
from src.core.security import hash_password, verify_password, create_access_token, get_current_user_id
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Register a new user (Farmer or Admin).
    - Validates email uniqueness
    - Hashes password securely
    - Creates user document in MongoDB
    - Returns JWT token and user details
    """
    users_collection = get_users_collection()
    
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_doc = {
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": user_data.role,
        "name": user_data.name,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    access_token = create_access_token(data={"sub": user_id, "role": user_data.role})
    
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        role=user_data.role,
        name=user_data.name,
        created_at=user_doc["created_at"]
    )
    
    return TokenResponse(access_token=access_token, user=user_response)

@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """
    Authenticate user with email and password.
    - Validates credentials
    - Returns JWT token for authenticated sessions
    - Includes user profile in response
    """
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id, "role": user["role"]})
    
    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        role=user["role"],
        name=user.get("name"),
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=access_token, user=user_response)

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, used by Swagger UI.
    """
    users_collection = get_users_collection()
    
    # username field is used for email
    user = await users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id, "role": user["role"]})
    
    # We construct a partial response matching TokenResponse, but TokenResponse requires 'user'
    # Swagger UI only really cares about the 'access_token', but our model requires 'user'.
    # We can fetch the user details to keep it consistent.
    
    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        role=user["role"],
        name=user.get("name"),
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=access_token, user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """
    Get current authenticated user's profile.
    - Requires valid JWT token
    - Returns user details without sensitive information
    """
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        role=user["role"],
        name=user.get("name"),
        created_at=user["created_at"]
    )
