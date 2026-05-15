# 测试用例说明

本目录包含基于 **TDD（测试驱动开发）** 理念的完整测试用例，用于在面试任务开发前明确接口契约与验收标准。

---

## 目录结构

```
tests/
├── conftest.py           # 测试基础设施（DB、Redis、TestClient、 fixtures）
├── test_auth.py          # 登录模块 TDD 用例
├── test_middleware.py    # 鉴权中间件 & 白名单 TDD 用例
├── test_address.py       # 业务接口 TDD 用例
└── README.md             # 本文件
```

---

## 测试分类

| 标记 | 说明 | 运行方式 |
|------|------|----------|
| `unit` | 纯单元测试，不依赖外部网络 | `pytest -m unit` |
| `integration` | 集成测试，依赖外部地址 API | `pytest -m integration` |
| `auth` | 登录相关测试 | `pytest -m auth` |
| `middleware` | 鉴权/白名单相关测试 | `pytest -m middleware` |
| `address` | 业务接口相关测试 | `pytest -m address` |

---

## 当前状态

> **注意**：项目代码尚未开发，所有测试目前处于 **占位/跳过** 状态。

### 开发流程

1. 参考 `docs/03-技术规划.md` 创建项目骨架
2. 逐一实现被测模块（见各测试文件头部的 **目标文件** 注释）
3. 取消 `conftest.py` 中的 TODO 注释，接入真实依赖
4. 运行 `pytest` 驱动开发，直至全部通过

---

## 常用命令

```bash
# 运行全部测试
pytest

# 仅运行单元测试（不调用外部 API）
pytest -m unit

# 仅运行登录模块测试
pytest -m auth -v

# 运行集成测试（需网络畅通）
pytest -m integration -v

# 显示测试覆盖率
pytest --cov=app --cov-report=term-missing
```

---

## conftest.py 说明

`conftest.py` 已预置以下 fixtures，开发完成后取消注释即可使用：

| Fixture | 作用 | 生命周期 |
|---------|------|----------|
| `event_loop` | 异步事件循环 | session |
| `db_engine` | 内存数据库引擎 | session |
| `db_session` | 独立 DB 会话（自动回滚） | function |
| `redis_client` | Redis 客户端（测试隔离） | session |
| `client` | httpx.AsyncClient 测试客户端 | function |
| `test_user` | 预置测试用户（test/123456） | function |
| `auth_headers` | 带有效 Token 的请求头字典 | function |
