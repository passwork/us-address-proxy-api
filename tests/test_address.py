"""
业务接口（美国地址生成）TDD 测试用例

目标文件（待开发）：
- app/api/address.py              — 业务路由
- app/services/address_service.py — 外部 API 调用封装
- app/core/exceptions.py          — 自定义业务异常

外部依赖：
- https://www.meiguodizhi.com/api/v1/dz
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.address


class TestAddressSuccess:
    """外部 API 正常时的成功场景"""

    @pytest.mark.integration
    async def test_address_endpoint_returns_address_field(self, client, auth_headers):
        """
        【正向】携带有效 Token 调用地址接口，返回 code=200，data.address 为对象。

        注意：此测试依赖外部网络，标记为 integration。
        若外部服务不可用，可跳过：pytest -m 'not integration'
        """
        resp = await client.get("/api/v1/address/generate", headers=auth_headers)
        body = resp.json()

        assert resp.status_code == 200
        assert body["code"] == 200
        assert body["msg"] == "success"
        assert isinstance(body["data"]["address"], dict)
        assert "Address" in body["data"]["address"]
        assert "City" in body["data"]["address"]

    @pytest.mark.unit
    async def test_address_service_calls_external_api_with_correct_payload(self, client, auth_headers):
        """
        【单元】验证调用外部 API 时，请求体严格为 {"path": "/", "method": "address"}。

        使用 unittest.mock 拦截 httpx.AsyncClient.post。
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "address": {"Address": "Mock St", "City": "MockCity"},
            "status": "ok"
        }
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)) as mock_post:
            resp = await client.get("/api/v1/address/generate", headers=auth_headers)

            assert resp.status_code == 200
            # 验证 post 被调用且参数正确
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args.kwargs
            assert call_kwargs["json"] == {"path": "/", "method": "address"}
            assert call_kwargs["headers"]["Referer"] == "https://www.meiguodizhi.com/"


class TestAddressFailure:
    """外部 API 异常时的降级与错误处理"""

    @pytest.mark.unit
    async def test_address_service_timeout_returns_500(self, client, auth_headers):
        """
        【降级】外部 API 超时时，返回 code=500，msg 提示服务不可用。
        """
        import app.services.address_service as addr_svc

        with patch.object(addr_svc.settings, "address_api_mock_on_failure", False):
            with patch("httpx.AsyncClient.post", side_effect=TimeoutError("Connection timed out")):
                resp = await client.get("/api/v1/address/generate", headers=auth_headers)
                body = resp.json()

                assert resp.status_code == 500
                assert body["code"] == 500
                assert "暂不可用" in body["msg"] or "timeout" in body["msg"].lower()

    @pytest.mark.unit
    async def test_address_service_http_error_returns_500(self, client, auth_headers):
        """
        【降级】外部 API 返回 5xx 时，同样返回 code=500。
        """
        import app.services.address_service as addr_svc
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("500 Internal Server Error")

        with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)):
            with patch.object(addr_svc.settings, "address_api_mock_on_failure", False):
                resp = await client.get("/api/v1/address/generate", headers=auth_headers)
                body = resp.json()

                assert resp.status_code == 500
                assert body["code"] == 500

    @pytest.mark.unit
    async def test_address_service_missing_address_field_returns_500(self, client, auth_headers):
        """
        【防御】外部 API 返回成功但缺少 address 字段，不应 KeyError 崩溃。
        """
        import app.services.address_service as addr_svc
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}  # 缺少 address
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)):
            with patch.object(addr_svc.settings, "address_api_mock_on_failure", False):
                resp = await client.get("/api/v1/address/generate", headers=auth_headers)
                body = resp.json()

                assert resp.status_code == 500
                assert body["code"] == 500

    @pytest.mark.unit
    async def test_address_service_returns_mock_on_failure(self, client, auth_headers):
        """
        【降级策略】当外部 API 失败时，若配置了 MOCK 开关，返回 Mock 数据保证可用性。
        """
        from unittest.mock import patch

        with patch("httpx.AsyncClient.post", side_effect=Exception("External API down")):
            resp = await client.get("/api/v1/address/generate", headers=auth_headers)
            body = resp.json()

            assert resp.status_code == 200
            assert body["code"] == 200
            assert isinstance(body["data"]["address"], dict)
            assert body["data"]["address"]["Address"] == "1600 Amphitheatre Parkway"


class TestAddressNoAuth:
    """未鉴权访问业务接口"""

    @pytest.mark.unit
    async def test_address_without_auth(self, client):
        """重复验证：无 Token 时返回 401（与 test_middleware.py 互补）。"""
        resp = await client.get("/api/v1/address/generate")

        assert resp.status_code == 401
        assert resp.json()["code"] == 401


class TestAddressDataIntegrity:
    """返回数据格式与内容校验"""

    @pytest.mark.integration
    async def test_address_response_matches_expected_schema(self, client, auth_headers):
        """
        【契约】返回结构必须严格符合：
        {"code": 200, "data": {"address": {...}}, "msg": "success"}
        """
        resp = await client.get("/api/v1/address/generate", headers=auth_headers)
        body = resp.json()

        assert set(body.keys()) == {"code", "data", "msg"}
        assert set(body["data"].keys()) == {"address"}
        assert isinstance(body["data"]["address"], dict)

    @pytest.mark.integration
    async def test_address_field_contains_us_address_components(self, client, auth_headers):
        """
        【语义】address 对象应包含典型的美国地址字段（至少验证核心字段存在）。
        """
        resp = await client.get("/api/v1/address/generate", headers=auth_headers)
        address = resp.json()["data"]["address"]

        core_fields = ["Address", "City", "State", "Zip_Code"]
        for field in core_fields:
            assert field in address, f"Missing field: {field}"
            assert isinstance(address[field], str)
            assert len(address[field]) > 0
