# 自动化测试框架学习项目

这是一个从零搭建 UI/API 自动化测试框架的配套学习项目，包含：

- `app/`：本地可部署的前后端被测系统（订单管理系统）。
- `automation/`：自动化测试框架，将在阶段一开始逐步搭建。
- `docs/`：学习路径与项目记忆。

## 被测系统

订单管理系统提供用户注册、登录，以及订单的新增、查询、分页搜索、修改、删除，并包含完整的成功与失败场景，供 UI 和 API 自动化练习。

### 快速开始

Windows（PowerShell）：

```powershell
.\start.ps1
```

macOS / Linux：

```bash
./start.sh
```

启动后访问：

- 前端页面：<http://127.0.0.1:8000/>
- 接口文档（OpenAPI）：<http://127.0.0.1:8000/docs>

### 主要接口

- `POST /api/auth/register`：注册
- `POST /api/auth/login`：登录
- `GET /api/orders`：订单列表（支持 `page`、`page_size`、`q` 查询）
- `POST /api/orders`：新增订单
- `GET /api/orders/{id}`：订单详情
- `PUT /api/orders/{id}`：修改订单
- `DELETE /api/orders/{id}`：删除订单

受保护接口需要请求头 `Authorization: Bearer <token>`。

## 学习路径

详细的七阶段学习路线见 [docs/learning-path.md](docs/learning-path.md)，进度与记忆见 [docs/project-memory.md](docs/project-memory.md)。
