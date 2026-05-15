# API 接口文档

> US Address Proxy Service — 用户鉴权与地址生成代理服务

---

## 环境信息

- **Base URL**: `http://localhost:8000`
- **API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Content-Type**: `application/json`

---

## 通用响应格式

所有接口（包括错误响应）均返回统一结构：

```json
{
  "code": 200,
  "data": {},
  "msg": "success"
}
```

### 错误码说明

| Code | 含义 | 场景 |
|------|------|------|
| 200 | 成功 | 通用 |
| 400 | 参数错误 / 业务逻辑错误 | 账号或密码错误 |
| 401 | 未授权 | Token 缺失、过期或无效 |
| 422 | 请求参数校验失败 | 缺少必填字段、类型不匹配 |
| 500 | 服务端错误 | 外部 API 超时、数据库异常 |

---

## 1. 登录接口

### POST `/api/v1/auth/login`

用户登录，成功后返回 Token。

**请求体**：

```json
{
  "account": "test",
  "pwd": "123456"
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| account | string | 是 | 登录账号，长度 1-64 |
| pwd | string | 是 | 密码，长度 1-128 |

**成功响应 (200)****：

```json
{
  "code": 200,
  "data": {
    "token": "A2dgY1R7lgHyShaILRkV40kiUmhZyHwAkva6m-LNXZA",
    "expires_in": 3600
  },
  "msg": "success"
}
```

**失败响应示例**：

- 账号或密码错误 (400)

```json
{
  "code": 400,
  "data": null,
  "msg": "账号或密码错误"
}
```

- 缺少必填字段 (422)

```json
{
  "code": 422,
  "data": null,
  "msg": "请求参数校验失败"
}
```

---

## 2. 美国地址生成接口

### GET `/api/v1/address/generate`

调用第三方美国地址生成器，返回地址信息。

**请求头**：

```http
Authorization: Bearer <token>
```

**成功响应 (200)****：

```json
{
  "code": 200,
  "data": {
    "address": {
      "Address": "4427 Kincheloe Road",
      "Address_Alias": "",
      "Birthday": "6/11/1979",
      "Browser_User_Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)...",
      "CVV2": "364",
      "City": "Portland",
      "Company_Name": "Dynatronics Accessories",
      "Company_Size": "29-50 employees",
      "Credit_Card_Number": "4916977754095978",
      "Credit_Card_Type": "Visa",
      "Educational_Background": "High school diploma or GED",
      "Employment_Status": "Leave of absence",
      "Expires": "02/2029",
      "Fax": "",
      "Full_Name": "Benai",
      "Full_Name_Tran": "拜奈伊",
      "GUID": "54d5f65b-822b-454a-a375-e56e45eb7916",
      "Gender": "Female",
      "Hair_Color": "Black",
      "Height": "6' 1\" (186cm)",
      "Monthly_Salary": "$5,800",
      "Occupation": "Public Relation, Teacher",
      "Password": "fgravZ8iR3Gw",
      "Security_Answer": "stimulationgood-sized",
      "Security_Question": "What is your dog's name?",
      "Social_Security_Number": "002-65-5404",
      "State": "OR",
      "State_Full": "Oregon",
      "System": "Windows 10",
      "Telephone": "503-527-5486",
      "Temporary_mail": "ztrjxirjbk@iubridge.com",
      "Title": "Mrs.",
      "Trans_Address": "",
      "Trans_Cn_Address": "",
      "Username": "flankuntested",
      "Website": "tmyvfjcyn.com",
      "Weight": "142.8lbs (64.8kg)",
      "Zip_Code": "97232",
      "rowkey": "6bfd5ed0-44e3-4f9a-b0c5-2330721da24f"
    }
  },
  "msg": "success"
}
```

**失败响应示例**：

- 未授权 (401)

```json
{
  "code": 401,
  "data": null,
  "msg": "未授权，缺少有效Token"
}
```

- Token 无效或过期 (401)

```json
{
  "code": 401,
  "data": null,
  "msg": "Token已过期或无效"
}
```

- 外部服务不可用 (500)

```json
{
  "code": 500,
  "data": null,
  "msg": "外部地址服务暂不可用"
}
```

---

## 3. 白名单接口（免鉴权）

以下接口无需携带 Token 即可访问：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/docs` | GET | Swagger UI 文档 |
| `/openapi.json` | GET | OpenAPI 规范 JSON |
| `/api/v1/auth/login` | POST | 登录接口 |

---

## Postman 测试步骤

### 步骤 1：登录获取 Token

```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "account": "test",
  "pwd": "123456"
}
```

从响应中提取 `data.token`。

### 步骤 2：调用地址生成接口

```http
GET http://localhost:8000/api/v1/address/generate
Authorization: Bearer <步骤1获取的token>
```

### 步骤 3：验证鉴权拦截

不带 `Authorization` Header 直接调用地址接口，应返回 401。

---

## 测试账号

| 账号 | 密码 | 昵称 |
|------|------|------|
| test | 123456 | TestUser |

可通过运行 `python scripts/init_db.py` 初始化测试账号。
