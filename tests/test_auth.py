"""
登录模块测试用例
"""

import pytest

pytestmark = pytest.mark.auth


class TestLoginEndpoint:
    """POST /api/v1/auth/login"""

    @pytest.mark.unit
    async def test_login_success_returns_token(self, client, test_user):
        """
        【正向】使用正确的账号密码登录，返回 code=200、token、过期时间。

        期望结构：
        {
          "code": 200,
          "data": {"token": "...", "expires_in": 3600},
          "msg": "success"
        }
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": test_user["plain_pwd"]
        })
        body = resp.json()

        assert resp.status_code == 200
        assert body["code"] == 200
        assert body["msg"] == "success"
        assert "token" in body["data"]
        assert "expires_in" in body["data"]
        assert isinstance(body["data"]["token"], str)
        assert len(body["data"]["token"]) > 0

    @pytest.mark.unit
    async def test_login_wrong_password_returns_400(self, client, test_user):
        """
        【异常】密码错误时，返回 code=400，不暴露具体是账号还是密码错。

        开发约束：
        - 必须做恒定时间比较（timing-safe），防止侧信道攻击
        - 响应体不包含 "user not found" 或 "password incorrect" 等区分性描述
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": "wrong_password"
        })
        body = resp.json()

        assert resp.status_code == 400
        assert body["code"] == 400
        assert body["data"] is None
        assert "账号或密码错误" in body["msg"]

    @pytest.mark.unit
    async def test_login_nonexistent_user_returns_400(self, client):
        """
        【异常】账号不存在时，同样返回 code=400，与密码错误不可区分。
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": "not_exist_user",
            "pwd": "any_password"
        })
        body = resp.json()

        assert resp.status_code == 400
        assert body["code"] == 400
        assert body["data"] is None

    @pytest.mark.unit
    async def test_login_missing_account_returns_422(self, client):
        """
        【参数校验】缺少 account 字段，FastAPI Pydantic 自动校验返回 422。
        """
        resp = await client.post("/api/v1/auth/login", json={
            "pwd": "123456"
        })

        assert resp.status_code == 422

    @pytest.mark.unit
    async def test_login_missing_pwd_returns_422(self, client):
        """
        【参数校验】缺少 pwd 字段，FastAPI Pydantic 自动校验返回 422。
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": "test"
        })

        assert resp.status_code == 422

    @pytest.mark.unit
    async def test_login_empty_string_pwd_returns_422(self, client, test_user):
        """
        【边界】密码为空字符串，Pydantic min_length=1 校验拦截，返回 422。
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": ""
        })
        body = resp.json()

        assert resp.status_code == 422
        assert body["code"] == 422


class TestTokenStorage:
    """Token 在 Redis 中的存储规则验证"""

    @pytest.mark.unit
    async def test_login_token_stored_in_redis(self, client, test_user, redis_client):
        """
        【数据一致性】登录成功后，token 必须写入 Redis，且可检索。

        期望的 Redis Key 设计：
        - key:   token:{token_value}
        - value: user_id
        - ttl:   TOKEN_EXPIRE_SECONDS（如 3600s）
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": test_user["plain_pwd"]
        })
        token = resp.json()["data"]["token"]

        value = await redis_client.get(f"token:{token}")
        assert value is not None
        assert str(test_user["id"]) == value

    @pytest.mark.unit
    async def test_token_expires_after_ttl(self, client, test_user, redis_client):
        """
        【过期策略】Token 在 Redis 中的 TTL 应与配置一致（如 3600s）。
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": test_user["plain_pwd"]
        })
        token = resp.json()["data"]["token"]
        ttl = await redis_client.ttl(f"token:{token}")
        assert ttl > 0
        assert ttl <= 3600


class TestPasswordSecurity:
    """密码安全策略验证"""

    @pytest.mark.unit
    async def test_password_never_returned_in_response(self, client, test_user):
        """
        【安全】任何接口（包括登录成功响应）都不得返回密码或密码哈希。
        """
        resp = await client.post("/api/v1/auth/login", json={
            "account": test_user["account"],
            "pwd": test_user["plain_pwd"]
        })
        raw_text = resp.text

        assert "pwd" not in raw_text.lower()
        assert "password" not in raw_text.lower()
        assert "$2b$" not in raw_text  # bcrypt 前缀

    @pytest.mark.unit
    async def test_password_is_hashed_in_db(self, test_user):
        """
        【安全】数据库中的 pwd 字段必须是 bcrypt 哈希，而非明文。
        """
        assert test_user["pwd"].startswith("$2b$")
        assert len(test_user["pwd"]) > 50


class TestLogoutEndpoint:
    """POST /api/v1/auth/logout"""

    @pytest.mark.unit
    async def test_logout_success_deletes_token(self, client, auth_headers, redis_client):
        """
        【正向】携带有效 Token 登出，返回 code=200，且 Redis 中 token 被删除。
        """
        token = auth_headers["Authorization"].replace("Bearer ", "")
        assert await redis_client.get(f"token:{token}") is not None

        resp = await client.post("/api/v1/auth/logout", headers=auth_headers)
        body = resp.json()

        assert resp.status_code == 200
        assert body["code"] == 200
        assert body["msg"] == "success"
        assert await redis_client.get(f"token:{token}") is None

    @pytest.mark.unit
    async def test_logout_without_auth_returns_401(self, client):
        """
        【异常】无 Token 登出返回 401。
        """
        resp = await client.post("/api/v1/auth/logout")
        body = resp.json()

        assert resp.status_code == 401
        assert body["code"] == 401

    @pytest.mark.unit
    async def test_logout_with_invalid_token_returns_401(self, client):
        """
        【异常】伪造 Token 登出返回 401。
        """
        resp = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer fake_token_123"}
        )
        body = resp.json()

        assert resp.status_code == 401
        assert body["code"] == 401

    @pytest.mark.unit
    async def test_token_invalidated_after_logout(self, client, auth_headers):
        """
        【主动失效】登出后再用原 Token 访问业务接口，应返回 401。
        """
        resp_logout = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert resp_logout.status_code == 200

        resp = await client.get("/api/v1/address/generate", headers=auth_headers)
        body = resp.json()

        assert resp.status_code == 401
        assert body["code"] == 401
