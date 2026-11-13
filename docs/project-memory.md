# 项目记忆

## 当前状态

- 当前阶段：阶段 2（API 自动化最小闭环）
- 更新时间：2026-11-13
- 状态：阶段二前三节课已完成，鉴权 service 已经学习者确认；第四节课准备实现订单 service

## 项目目标

从零搭建面向线上产品的 UI/API 自动化测试框架，并提供本地可部署的前后端被测系统，按 `docs/learning-path.md` 分七阶段推进。

## 已完成

- 学习项目已迁移到 `E:\python-pytest-ci-cd-ui-api`，旧 C 盘目录已删除。
- 创建项目级 AI 教学规范 `AGENTS.md`。
- 创建七阶段学习路径 `docs/learning-path.md`。
- 搭建被测系统（订单管理系统）：
  - 后端：FastAPI + SQLite，注册/登录/鉴权 + 订单 CRUD、分页搜索。
  - 前端：原生 HTML/JS，登录/注册、订单列表与表单，元素带 `data-testid`。
  - 启动脚本：`start.ps1`、`start.sh`。
- 通过冒烟自测脚本 `work/smoke_test.py` 验证前后端核心流程。
- 学习者已分别完成浏览器端完整业务验收和接口文档验收，确认阶段 0 通过。
- git 仓库已初始化并完成首次提交（提交信息：`接触骨架搭建`）。
- 环境工具链已修复：
  - 发现本机已有 `uv 0.12.9`，但 `C:\Users\Administrator\.local\bin` 未加入用户 PATH，已加入（新终端生效）。
  - 使用 uv 将依赖安装到根目录 `venv/`，不再依赖全局 Python。
  - 新增 `requirements-dev.txt`（运行时依赖 + 冒烟自测所需 httpx）与锁文件 `requirements-dev.lock`。
  - `start.ps1`、`start.sh` 已改为优先使用 `venv/`，缺失时回退到全局 `python`。
- 进入本节课前 Git 工作区干净，最新提交为 `dec5082`（补充 PowerShell 执行策略说明）。
- 阶段一第一节课已完成：
  - 使用 `uv 0.12.9` 将 `automation/` 初始化为独立 Python 项目。
  - 生成 `automation/pyproject.toml` 与 `automation/uv.lock`。
  - 将 `pytest 9.2.0` 安装到 `automation/.venv`，并记录为开发依赖。
  - 创建 `automation/tests/`、`automation/config/`、`automation/core/`、`automation/conftest.py`、`automation/pytest.ini`。
  - 创建单条冒烟用例 `automation/tests/test_smoke.py`。
  - `uv run pytest -v` 通过：1 passed；`uv lock --check` 通过。
- 阶段一第二节课已完成：
  - 新增 `automation/tests/test_assertions.py`，包含 4 条基础用例。
  - 练习行为型命名、相等断言、成员断言、大小比较和字典整体比较。
  - 通过临时制造 `assert -1 > 0` 失败，确认 pytest 能显示实际值、预期关系、文件与行号。
  - 失败演示后已恢复正确数据，全部 5 条用例最终通过。
- 阶段一第三节课已完成：
  - 在 `automation/conftest.py` 中定义 session 级 `session_context` fixture。
  - 定义依赖 `session_context` 的 function 级 `function_context` fixture。
  - 新增 `automation/tests/test_fixtures.py`，通过参数名完成 fixture 依赖注入。
  - 使用 `pytest -s -v` 观察到 session fixture 只 setup/teardown 一次，function fixture 对每条用例各执行一次。
  - 全套测试通过：7 passed。
- 阶段一第四节课已完成：
  - 新增 `automation/tests/test_parametrize.py`。
  - 使用 `@pytest.mark.parametrize` 让同一个测试函数驱动 5 组标题、金额和期望结果。
  - 使用 `ids` 生成 normal-order、minimum-positive-amount、blank-title、zero-amount、negative-amount 等可读测试 ID。
  - 参数化专项测试通过：5 passed；全套测试通过：12 passed。
- 阶段一第五节课已完成：
  - 在 `automation/pytest.ini` 注册 `smoke` 与 `regression` 自定义 marker。
  - 启用 `--strict-markers`，拼错或未注册的 marker 会直接报错。
  - 第五节课初始验收时，`test_smoke.py` 标记为 `smoke`，其余测试模块标记为 `regression`。
  - `-m smoke`：1 passed、11 deselected。
  - `-m regression`：11 passed、1 deselected。
  - `-m "smoke or regression"` 与无筛选全套执行均为 12 passed。
  - 学习者后续为 `test_assertions.py` 增加了 `smoke` 标记，并保留原有 `regression` 标记；当前该模块同时属于两组。
- 阶段一第六节课已完成：
  - 使用 `-k "order and not parametrize"` 验证名称表达式筛选：3 passed、9 deselected。
  - 使用临时演示文件验证 `--maxfail=1`：首个失败后输出 stopping after 1 failures，后续测试未执行。
  - 临时失败演示文件已在验证后删除。
  - 删除演示文件后重新运行全套测试：12 passed。
- 阶段一第七节课与阶段验收已完成：
  - 使用 uv 将 `pytest-html 4.2.0` 安装为开发依赖，并更新 `uv.lock`。
  - `pytest.ini` 自动生成 `reports/report.html`，并通过 `--self-contained-html` 生成可独立打开的报告。
  - 学习者完成 HTML 报告与命令行环境排错验收：直接执行全局 `pytest` 不会加载项目插件，项目统一使用 `uv run pytest`。
  - `-m smoke` 复验：5 passed、7 deselected。
  - `-k "order and not parametrize"` 复验：3 passed、9 deselected。
  - 全套最终复验：12 passed，HTML 报告同步生成。
  - `uv lock --check` 通过；顶层开发依赖为 pytest 9.2.0 与 pytest-html 4.2.0。
  - `reports/report.html` 已确认被 `.gitignore` 排除。
- 阶段一代码与锁文件已提交：`2dc7aa4 搭建阶段一pytest自动化框架`。
- 阶段二第一节课已完成：
  - 在 `automation/` 中新增运行时依赖 `httpx>=0.28.1` 并更新 `uv.lock`。
  - 创建 `automation/core/__init__.py`，公开 `APIClient`。
  - 创建 `automation/core/api_client.py`，实现 base_url、超时、默认请求头、常用 HTTP 方法和请求响应耗时日志。
  - 验证 `/openapi.json` 返回 200，未授权 `/api/orders` 返回 401 且响应可被调用方检查。
  - 阶段一原有 12 条测试保持通过。
  - 已提交为 `877f675 完成基础 APIClient 类`。
- 阶段二第二节课已完成并经学习者确认：
  - 创建 `automation/core/exceptions.py`，包含 `AutomationError`、`APIClientError` 与 `APITransportError`。
  - 创建 `automation/core/logger.py`，统一 `automation.*` logger、输出格式与敏感字段递归脱敏。
  - 改造 `APIClient` 使用统一 logger，并把 httpx 传输错误转换为 `APITransportError`。
  - 更新 `core/__init__.py` 导出客户端、异常、日志配置和脱敏函数。
  - 确认 4xx/5xx HTTP 响应仍原样返回，网络传输失败才抛框架异常。
- 阶段二第三节课已完成并经学习者确认：
  - 扩展 `APIResponseError`，保留非预期 HTTP 状态码和响应体。
  - 创建并导出 `automation/services/auth_service.py` 中的 `AuthService`。
  - `register()` 与 `login()` 返回原始 `httpx.Response`，便于测试 201、401、409、422。
  - `get_token()` 校验 200、JSON 对象和非空 token，失败时抛 `APIResponseError`。
  - 通过真实注册、登录、错误密码和 token 获取流程完成验证。

## 待办

- 创建 `automation/services/order_service.py` 并更新服务层导出。
- 为创建、详情、列表、修改和删除订单提供统一 Bearer 鉴权与业务方法。

## 项目结构快照

- `AGENTS.md`：AI 教学规范与项目约束。
- `app/backend/`：FastAPI 后端。
- `app/frontend/`：前端静态资源。
- `automation/`：独立 uv 项目与 pytest 自动化框架。
- `automation/tests/`：pytest 用例目录。
- `automation/config/`：后续环境与测试配置目录。
- `automation/core/`：后续底层能力封装目录。
- `docs/learning-path.md`、`docs/project-memory.md`：教学文档。

## 已知问题

- `uv` 的 PATH 修改只对本次修改之后新开的终端生效；旧终端需要重开后才能直接执行 `uv`。
- PowerShell 若提示脚本被禁用，按 README 中的执行策略说明使用 `Process Bypass` 或 `CurrentUser RemoteSigned`。
- Codex 当前终端的 PATH 尚未识别 `uv`；实际执行时可使用 uv 的显式安装路径，或由学习者在自己的新 PowerShell 中执行。
- 在 `automation/` 中直接执行 `pytest` 会命中全局 Python 3.11 的 pytest 8.4.2，未加载项目 `.venv` 中的 pytest-html；应使用 `uv run pytest` 或项目的虚拟环境解释器。
- `automation/pyproject.toml` 声明 `requires-python = ">=3.11"`；uv 当前为独立环境选择了 Python 3.12.14，这与根目录被测系统的 Python 3.11.5 环境相互隔离。
- PyCharm 当前可能把 `from core import APIClient, APIResponseError` 标红，因为尚未把 `automation/` 标记为 Sources Root；该问题需以 `uv run python` 的实际导入结果为准，不应安装名为 `APIClient` 的包。
- `auth_service.py` 中存在未使用的 `NoReturn` 导入，仅为静态检查提示，不影响运行，可在下一课顺手清理。

## 下一步计划

1. 实现 `services/order_service.py`，封装订单创建、详情、列表、修改和删除。
2. 下一课在 `conftest.py` 提供 base_url、API client 和登录 token fixture。
3. 随后编写正式 `tests/api/test_auth.py` 与 `tests/api/test_order.py`。

## 重要变更

- 新增依赖文件：`requirements-dev.txt`、`requirements-dev.lock`。
- 启动脚本改为自动选择 `venv/` 中的解释器。
- 被测系统依赖已锁定，环境可复现。
- 新增独立 uv 工程：`automation/pyproject.toml`、`automation/uv.lock`。
- 新增 pytest 基础配置、共享配置入口、基础目录和首条冒烟用例。
- 新增 4 条基础断言用例，当前共有 5 条通过的 pytest 用例。
- `conftest.py` 新增 function/session 两级共享 fixture，并新增 2 条 fixture 用例；当前共有 7 条通过的 pytest 用例。
- 新增 1 个参数化测试函数及 5 组数据，当前共有 12 条通过的 pytest 测试项。
- `pytest.ini` 新增 `smoke`、`regression` marker 注册及 `--strict-markers`；测试模块已按用途完成标记。
- 已验证 `-k` 名称筛选和 `--maxfail=1` 失败提前停止，未保留临时失败演示文件。
- 新增开发依赖 `pytest-html 4.2.0`，默认生成自包含 HTML 报告。
- 阶段一形成 12 条通过的 pytest 测试项，具备 fixture、参数化、marker、筛选和 HTML 报告能力。
- `AGENTS.md` 新增后续阶段“仅指导、不代做”固定规则，并明确 `docs/project-memory.md` 仍由 AI 持续维护。
- 阶段一收尾提交：`d53f800 补充后续阶段不代做教学规则`。
- 阶段二第一节课完成：新增 httpx、统一 `APIClient` 与 core 包入口，提交为 `877f675`。
- 阶段二第二节课完成：把日志配置、敏感信息脱敏和异常层次从 API 客户端中解耦；学习者确认通过。
- 阶段二第三节课完成：新增 `APIResponseError`、`services` 包和 `AuthService`；学习者确认通过。
- 阶段二第四节课开始：建立 `OrderService`，把鉴权 header 与订单 CRUD 细节集中到服务层。
