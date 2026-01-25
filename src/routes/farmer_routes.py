from fastapi import APIRouter, HTTPException, status, Depends
from src.models.farmer_model import FarmerProfileCreate, FarmerProfileResponse
from src.database.mongo import get_farmers_collection, get_users_collection
from src.core.security import get_current_user_id
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/farmer", tags=["Farmer Profile"])

async def verify_farmer_role(user_id: str = Depends(get_current_user_id)) -> str:
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user or user.get("role") != "Farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Farmer role required."
        )
    return user_id

@router.post("/profile", response_model=FarmerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_farmer_profile(
    profile_data: FarmerProfileCreate,
    user_id: str = Depends(verify_farmer_role)
):
    """
    Create or update farmer profile.
    - Farmer-only endpoint (requires Farmer role)
    - Upserts profile data (creates if not exists, updates if exists)
    - Links profile to authenticated user
    """
    farmers_collection = get_farmers_collection()
    
    existing_profile = await farmers_collection.find_one({"user_id": user_id})
    
    if existing_profile:
        update_data = profile_data.dict()
        update_data["updated_at"] = datetime.utcnow()
        
        await farmers_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        updated_profile = await farmers_collection.find_one({"user_id": user_id})
        
        return FarmerProfileResponse(
            id=str(updated_profile["_id"]),
            user_id=updated_profile["user_id"],
            district=updated_profile["district"],
            experience_years=updated_profile.get("experience_years"),
            farm_size_acres=updated_profile.get("farm_size_acres"),
            phone_number=updated_profile.get("phone_number"),
            created_at=updated_profile["created_at"],
            updated_at=updated_profile["updated_at"]
        )
    else:
        profile_doc = {
            "user_id": user_id,
            **profile_data.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await farmers_collection.insert_one(profile_doc)
        
        return FarmerProfileResponse(
            id=str(result.inserted_id),
            user_id=user_id,
            district=profile_data.district,
            experience_years=profile_data.experience_years,
            farm_size_acres=profile_data.farm_size_acres,
            phone_number=profile_data.phone_number,
            created_at=profile_doc["created_at"],
            updated_at=profile_doc["updated_at"]
        )

@router.get("/profile", response_model=FarmerProfileResponse)
async def get_farmer_profile(user_id: str = Depends(verify_farmer_role)):
    """
    Get farmer's profile information.
    - Farmer-only endpoint
    - Returns stored profile data for authenticated farmer
    """
    farmers_collection = get_farmers_collection()
    
    profile = await farmers_collection.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Please create a profile first."
        )
    
    return FarmerProfileResponse(
        id=str(profile["_id"]),
        user_id=profile["user_id"],
        district=profile["district"],
        experience_years=profile.get("experience_years"),
        farm_size_acres=profile.get("farm_size_acres"),
        phone_number=profile.get("phone_number"),
        created_at=profile["created_at"],
        updated_at=profile["updated_at"]
    )
