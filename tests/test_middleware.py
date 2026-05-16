"""
鉴权中间件与白名单测试用例
"""

import pytest

pytestmark = pytest.mark.middleware


class TestWhitelist:
    """白名单接口应免鉴权直接访问"""

    @pytest.mark.unit
    async def test_docs_endpoint_no_token(self, client):
        """Swagger UI (/docs) 必须在白名单中。"""
        resp = await client.get("/docs")
        assert resp.status_code == 200
        assert "swagger" in resp.text.lower() or "openapi" in resp.text.lower()

    @pytest.mark.unit
    async def test_openapi_endpoint_no_token(self, client):
        """OpenAPI JSON (/openapi.json) 必须在白名单中。"""
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        assert "openapi" in resp.text.lower()

    @pytest.mark.unit
    async def test_login_endpoint_no_token(self, client):
        """登录接口 (/api/v1/auth/login) 必须在白名单中。"""
        resp = await client.post("/api/v1/auth/login", json={
            "account": "any",
            "pwd": "any"
        })
        # 即使账号密码错，也应该是 400，而不是 401（说明鉴权没拦截）
        assert resp.status_code in (200, 400)
        assert resp.status_code != 401


class TestAuthMiddleware:
    """非白名单接口必须携带有效 Token"""

    @pytest.mark.unit
    async def test_address_without_token_returns_401(self, client):
        """
        【拦截】未携带 Token 访问业务接口，返回 401。
        """
        resp = await client.get("/api/v1/address/generate")
        body = resp.json()

        assert resp.status_code == 401
        assert body["code"] == 401
        assert "未授权" in body["msg"] or "Unauthorized" in body["msg"]

    @pytest.mark.unit
    async def test_address_with_invalid_token_returns_401(self, client):
        """
        【拦截】携带伪造/格式错误的 Token，返回 401。
        """
        resp = await client.get(
            "/api/v1/address/generate",
            headers={"Authorization": "Bearer fake_token_12345"}
        )
        body = resp.json()

        assert resp.status_code == 401
        assert body["code"] == 401

    @pytest.mark.unit
    async def test_address_with_malformed_header_returns_401(self, client):
        """
        【边界】Authorization Header 格式错误（如缺少 Bearer 前缀）。
        """
        resp = await client.get(
            "/api/v1/address/generate",
            headers={"Authorization": "Basic dGVzdDoxMjM0NTY="}
        )
        body = resp.json()

        assert resp.status_code == 401
        assert body["code"] == 401

    @pytest.mark.unit
    async def test_address_with_valid_token_succeeds(self, client, auth_headers):
        """
        【放行】携带正确 Token 访问业务接口，返回 200。
        """
        resp = await client.get("/api/v1/address/generate", headers=auth_headers)

        # 只要外部服务或 Mock 正常，应该返回 200
        assert resp.status_code == 200
        assert resp.json()["code"] == 200

    @pytest.mark.unit
    async def test_expired_token_returns_401(self, client, test_user, redis_client):
        """
        【过期】Token 在 Redis 中过期或被删除后，再次访问应返回 401。

        测试策略：
        1. 登录获取 token
        2. 在 Redis 中删除该 token（模拟过期）
        3. 携带该 token 访问业务接口
        4. 期望 401
        """
        resp_login = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": test_user["plain_pwd"]
        })
        token = resp_login.json()["data"]["token"]
        await redis_client.delete(f"token:{token}")

        resp = await client.get("/api/v1/address/generate", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.json()["code"] == 401


class TestResponseUniformity:
    """全局响应格式统一性验证"""

    @pytest.mark.unit
    async def test_all_responses_contain_code_data_msg(self, client):
        """
        【格式】任意接口（包括 401、404、422）返回的 JSON 都必须包含 code/data/msg 字段。
        """
        # 测试 401
        resp_401 = await client.get("/api/v1/address/generate")
        body_401 = resp_401.json()
        assert "code" in body_401
        assert "data" in body_401
        assert "msg" in body_401

        # 测试 422
        resp_422 = await client.post("/api/v1/auth/login", json={})
        body_422 = resp_422.json()
        assert "code" in body_422
        assert "data" in body_422
        assert "msg" in body_422

        # 测试 404
        resp_404 = await client.get("/api/v1/not_exist")
        body_404 = resp_404.json()
        assert "code" in body_404
        assert "data" in body_404
        assert "msg" in body_404
