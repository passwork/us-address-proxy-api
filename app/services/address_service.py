import httpx

from app.config import settings

MOCK_ADDRESS = {
    "Address": "1600 Amphitheatre Parkway",
    "City": "Mountain View",
    "State": "CA",
    "State_Full": "California",
    "Zip_Code": "94043",
    "Telephone": "650-253-0000",
    "Full_Name": "Mock User",
    "Gender": "Male",
}


async def fetch_us_address() -> dict:
    try:
        async with httpx.AsyncClient(timeout=settings.address_api_timeout) as client:
            resp = await client.post(
                settings.address_api_url,
                headers={"Referer": settings.address_api_referer},
                json={"path": "/", "method": "address"},
            )
            resp.raise_for_status()
            data = resp.json()
            address = data.get("address")
            if not address or not isinstance(address, dict):
                raise ValueError("外部API返回缺少address字段")
            return address
    except Exception:
        if settings.address_api_mock_on_failure:
            return MOCK_ADDRESS.copy()
        from app.core.exceptions import BizException
        raise BizException(code=500, msg="外部地址服务暂不可用")
