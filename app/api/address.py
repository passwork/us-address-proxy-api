from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.schemas import AddressResponse
from app.services.address_service import fetch_us_address

router = APIRouter(prefix="/api/v1/address", tags=["Address"])


@router.get("/generate", response_model=AddressResponse)
async def generate_address(_user_id: str = Depends(get_current_user)):
    address = await fetch_us_address()
    return AddressResponse(code=200, data={"address": address}, msg="success")
