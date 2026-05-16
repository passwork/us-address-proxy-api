# US Address Proxy Service

基于 FastAPI 的美国地址生成代理服务，提供用户鉴权与第三方地址 API 代理能力。

## 技术栈

- **Python**: 3.11 / 3.12（推荐），**不支持 3.13+**
- **Web 框架**: FastAPI 0.111.0
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (async)
- **缓存/会话**: Redis
- **密码哈希**: bcrypt
- **外部请求**: httpx
- **测试**: pytest + pytest-asyncio + fakeredis

## 快速启动（Docker Compose）

> 推荐方式，无需安装 Python、Redis 等依赖。

### 环境要求

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows / macOS / Linux)

### 启动步骤

```bash
# 1. 克隆项目
git clone https://github.com/passwork/us-address-proxy-api.git
cd us-address-proxy-api

# 2. 启动全栈服务（包含 PostgreSQL + Redis + App）
docker-compose up --build

# 3. 等待日志出现以下信息即表示启动成功：
# us_address_app  | Created user: test
# us_address_app  | INFO:     Application startup complete.
# us_address_app  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

服务启动后：
- API 文档: http://localhost:8000/docs
- OpenAPI 规范: http://localhost:8000/openapi.json
- 测试账号: `test` / `123456`

## 本地开发启动

> 适用于已安装 Python 3.11+ 且本地已运行 PostgreSQL 与 Redis 的环境。

### 环境准备

```bash
# 启动 PostgreSQL 与 Redis（如未安装，可用 Docker 快速启动）
docker run -d -p 5432:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=us_address_proxy postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

### 一键脚本

```bash
# Linux / macOS
bash scripts/setup_venv.sh

# Windows PowerShell
.\scripts\setup_venv.ps1
```

脚本会自动创建 venv、安装依赖并运行测试。

### 手动步骤

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate        # Linux/Mac
# .\venv\Scripts\activate       # Windows
pip install -r requirements.txt

# 2. 初始化测试数据
python scripts/init_db.py

# 3. 启动服务
uvicorn app.main:app --reload --port 8000
```

## Postman 测试

项目已提供配套的 Postman Collection：

- 文件路径: `docs/US-Address-Proxy-API.postman_collection.json`
- 导入方式: Postman → Import → 选择上述文件
- 包含用例: 登录、地址生成、鉴权拦截、参数校验、白名单验证

详细测试步骤请参考 [docs/运行指南.md](docs/运行指南.md)。

## API 接口文档

完整的接口文档请参阅 [docs/api.md](docs/api.md)，包含：

- 请求/响应示例
- 错误码说明
- Postman 手动测试步骤

## 项目结构

```
.
├── app/
│   ├── api/           # 路由层 (auth, address)
│   ├── core/          # 核心组件 (security, exceptions, whitelist, redis)
│   ├── services/      # 业务逻辑 (address_service)
│   ├── config.py      # 配置管理
│   ├── database.py    # 数据库引擎
│   ├── models.py      # ORM 模型
│   ├── schemas.py     # Pydantic 模型
│   ├── deps.py        # 依赖注入
│   └── main.py        # FastAPI 入口
├── tests/             # TDD 测试套件 (28 个用例)
├── docs/              # 项目文档 + Postman Collection
├── scripts/           # 数据初始化 + venv 安装脚本
├── alembic/           # 数据库迁移
├── Dockerfile         # Docker 镜像构建
├── docker-compose.yml # Docker Compose 编排
└── requirements.txt   # Python 依赖
```

## 测试

```bash
pytest -v
```

28 个测试用例覆盖登录鉴权、地址代理、中间件白名单、异常降级等场景。

## License

MIT
