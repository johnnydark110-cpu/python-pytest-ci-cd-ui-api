# 项目记忆

## 当前状态

- 当前阶段：阶段 4（UI 自动化与页面对象）
- 更新时间：2026-11-17
- 状态：阶段三已完成、提交并确认通过；阶段四第一节课进行中，已选定 Playwright，准备安装 Python 包、Chromium 浏览器并验证启动与关闭

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
  - 鉴权、异常与客户端相关提交为 `11562b1`。
- 阶段二第四节课已完成并经学习者确认：
  - 创建 `automation/services/order_service.py`，统一携带 Bearer token。
  - 实现 `create_order()`、`get_order()`、`list_orders()`、`update_order()`、`delete_order()`。
  - 所有订单方法返回原始 `httpx.Response`，便于验证 201、200、204、401、404 和 422。
  - 验证新增、详情、搜索列表、修改、未授权、删除及删除后 404 的完整流程。
  - 服务层导出同时包含 `AuthService` 与 `OrderService`。
  - 已提交为 `1f78b61 添加orderservice.py模块`。
- 阶段二第五节课已完成并经学习者确认：
  - `conftest.py` 新增 session 级 `base_url`、`api_client`、`auth_service` fixture。
  - 新增 function 级 `auth_user`、`token`、`order_service` fixture。
  - `base_url` 支持通过 `API_BASE_URL` 环境变量切换环境。
  - `api_client` 复用会话连接池并通过上下文管理器关闭。
  - `auth_user` 使用随机用户名隔离测试数据；`token` 自动注册并登录。
  - 临时 wiring 测试验证真实鉴权与订单列表访问通过，随后已从工作区删除。
- 阶段二第六节课已完成并经学习者确认：
  - 创建 `automation/tests/api/test_auth.py`，模块标记为 `regression`。
  - 覆盖注册成功、重复用户名、登录成功、错误密码、参数校验失败、有效 token 和无效 token。
  - 鉴权专项测试 7 passed；全套测试 19 passed；`-m regression` 18 passed。
  - 所有 API 请求均通过 `AuthService` 或 `OrderService`，测试中未出现裸 HTTP 调用。
- 阶段二第七节课已完成并经学习者确认：
  - 创建 `automation/tests/api/test_order.py`，覆盖创建、详情、分页搜索、部分修改、删除和用户隔离。
  - 覆盖零金额、负金额和非法状态的 422 响应。
  - 订单专项 9 passed；API 中共 16 条用例；完整测试 28 passed；`-m regression` 27 passed、1 deselected。
  - 已提交为 `e2c45f7 添加订单的API测试用例`。
- 阶段二第八节课与阶段验收已完成并经学习者确认：
  - `logger.py` 新增 `format_log_data()`，统一脱敏并格式化多行 JSON。
  - `APIClient` 记录请求方法、URL、查询参数、有效请求头、请求体、响应状态、响应头、响应体和耗时。
  - 密码、token、Authorization、Cookie 等敏感字段统一显示为 `***REDACTED***`。
  - 通过故意失败的临时用例确认 pytest 会展示完整请求响应上下文，随后已删除临时测试。
  - 阶段二验收结果：API 16 passed、全套 28 passed、regression 27 passed、1 deselected。
  - 已提交为 `3d32010 增加日志数据格式化函数 记录完整请求和响应`。
- 阶段三第一节课已完成并经学习者确认：
  - 安装并锁定 `pydantic-settings 2.16.3` 与 PyYAML。
  - 创建 `automation/config/settings.py` 与 `config/__init__.py`。
  - `Settings` 支持 `environment`、`base_url`、`timeout_seconds`、`verify_ssl` 类型校验。
  - `from_yaml()` 支持缺失文件、非对象 YAML、未知字段和非法类型的明确错误。
  - 支持 `AUTOMATION_ENVIRONMENT`、`AUTOMATION_BASE_URL`、`AUTOMATION_TIMEOUT_SECONDS`、`AUTOMATION_VERIFY_SSL` 环境变量覆盖。
  - 验证合法 YAML、非法 YAML 和 URL 规范化行为；`AnyHttpUrl` 的字符串形式会补根路径 `/`。
- 阶段三第二节课已完成并经学习者确认：
  - 创建 `config/dev.yaml`：本地 `127.0.0.1:8000`、10 秒超时、SSL 校验开启。
  - 创建 `config/staging.yaml`：本地模拟 `127.0.0.1:8001`、20 秒超时、SSL 校验开启。
  - 两份 YAML 均可通过 `Settings.from_yaml()` 加载并完成类型校验。
  - `AUTOMATION_TIMEOUT_SECONDS` 可覆盖 staging 的 YAML 超时。
  - 临时加载脚本已删除，配置只包含非敏感信息。
  - 已提交为 `34f44ef 创建开发环境配置 创建预发布环境配置`。
- 阶段三第三节课已完成并经学习者确认：
  - `conftest.py` 已注册 `--env`，支持 `dev`、`staging`，默认 `dev`。
  - 已增加 session 级 `settings` fixture，并根据 `--env` 加载 `config/<env>.yaml`。
  - `base_url` 已改为从 `Settings.base_url` 派生。
  - `APIClient` 已增加 `verify_ssl` 参数，并在内部把 `timeout` 和 `verify` 传给 `httpx.Client`。
  - 新增 `tests/test_config_wiring.py`，同时验证 `Settings`、`base_url` 和 `api_client` 的地址、超时与 SSL 配置。
  - 提交为 `a67c41d 添加setting对象Session范围初始化的fixture，修改APIClient在构造方法中添加setting配置`。
  - 学习者补齐 `api_client` fixture，把 `settings.timeout_seconds` 与 `settings.verify_ssl` 显式传给 `APIClient`。
  - dev 与 staging 配置接线专项均通过，学习者确认第三课完成。
  - 当前工作区中 `automation/conftest.py` 的第三课修正尚未提交；最近提交仍为 `a67c41d`。
- 阶段三第四节课已完成并经学习者确认：
  - 已创建 `automation/testdata/orders.yaml`，包含 6 组订单创建数据。
  - 已创建 `automation/core/yaml_loader.py` 和 `automation/tests/api/test_order_data_driven.py`。
  - `core/__init__.py` 已导出 `load_yaml_test_cases`。
  - 加载器类型注解已修正为 `list[dict[str, Any]]`。
  - 数据驱动测试已增加模块级 `regression` 标记。
  - 学习者确认数据驱动专项 6 passed、regression 34 passed、1 deselected、全套 35 passed。
  - 当前新增与修改文件尚未提交；最近提交仍为 `a67c41d`。
- 阶段三第五节课已完成并经学习者确认：
  - 安装并锁定 `allure-pytest 2.16.2` 开发依赖。
  - 安装 Allure Commandline 2.46.2 与 Temurin JRE 21，并解决终端 PATH 与 VS Code 继承旧环境的问题。
  - 创建 `core/allure_utils.py`，通过 `format_log_data()` 脱敏后附加 JSON。
  - `APIClient.request()` 增加 `allure.step()`，每次请求自动附加“请求上下文”和“响应上下文”。
  - `OrderService.create_order()` 增加 `@allure.step("创建订单")`。
  - 数据驱动用例增加 feature、story、动态 title 和“校验订单创建响应” step。
  - `pyproject.toml` 配置 Ruff `known-first-party`，`ruff check --select I001 automation` 通过。
  - 已生成 `automation/allure-results`，并通过 `allure serve` 检查步骤、附件和敏感信息脱敏。
- 阶段三第六节课已完成并经学习者确认：
  - 创建 `core/request_context.py`，使用 `ContextVar` 按测试保存请求响应历史，并在记录时脱敏。
  - `conftest.py` 增加 autouse fixture，在每条测试开始前创建历史、结束后清理。
  - `conftest.py` 增加 `pytest_runtest_makereport` hook，仅在失败时附加汇总 JSON。
  - `APIClient` 已把正常响应和传输异常登记到当前测试的历史列表。
  - 临时失败用例已验证报告包含注册、登录、订单创建请求及“失败上下文（call）”附件，随后已删除。
  - 学习者确认第六课验收通过。
- 阶段三总验收已完成并经学习者确认：
  - `--env=dev` 与 `--env=staging` 配置切换、YAML 数据驱动、Allure step/attachment、失败自动上下文和配置错误提示均按阶段验收流程检查。
  - 临时失败用例 `tests/api/test_failure_context_demo.py` 已删除，不存在于当前工作区。
  - 学习者确认阶段三正式完成。
  - Ruff 的 F401 与 PYI034 已清理，`ruff check automation` 通过。
  - 阶段三全部代码已提交为 `355ed4b 完整最终allure报告功能`，当前工作区干净。

## 待办

- 使用 uv 将 `playwright` 安装为 `automation/` 的开发依赖并更新 `uv.lock`。
- 执行 `playwright install chromium` 安装 Chromium 浏览器运行时。
- 创建临时验证脚本，确认无头 Chromium 能启动、打开本地 HTML、读取标题并正确关闭。

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
- VS Code 当前 `.vscode/settings.json` 与 `launch.json` 仍按根目录 `.venv`、根目录 `tests` 和根目录导入路径配置；必须选择 `automation/.venv/Scripts/python.exe`，把 `automation/` 加入 Pylance 搜索路径，并使用 `automation/` 作为 pytest 工作目录。
- Pydantic `AnyHttpUrl` 会把无路径 URL 规范化为带根路径 `/` 的形式；比较 URL 时应使用 `str(settings.base_url).rstrip("/")`，不能要求其字符串不带末尾 `/`。
- pytest 收集阶段会对 YAML 数据列表求值；YAML 语法、顶层类型或用例 ID 有问题时，会在收集阶段直接报错，应先修复数据文件再运行用例。
- `allure-pytest 2.16.2` 已加入 `automation/pyproject.toml`、`uv.lock` 并安装到 `automation/.venv`。
- VS Code 必须以 `automation/` 作为 pytest 工作目录并使用 `automation/.venv`；若启动时间早于 Java/Allure 的 PATH 修改，需要完整重启 VS Code 才能让新终端继承系统环境。
- 附件必须继续使用现有 `redact_data()` 脱敏，不能直接附加 Authorization、密码或 token 明文。
- Eclipse Temurin JRE 21 已安装到 `C:\Program Files\Eclipse Adoptium\jre-21.0.13.9-hotspot`，系统 PATH 和 `JAVA_HOME` 已正确配置；安装前已打开的 PowerShell 不会自动继承新 PATH，执行 `java --version` 前需要重开终端或在当前会话临时加载 Java 的 `bin`。
- Allure Commandline 2.46.2 已安装到 `C:\Users\Administrator\AppData\Local\Programs\allure-commandline\2.46.2\allure-2.46.2`；若新终端提示找不到 `allure`，先把其 `bin` 目录加入用户 PATH，并完整重启 VS Code。
- 失败上下文必须按测试隔离并在测试结束后清理，不能让上一条测试的请求混入下一条测试。
- `automation/pyproject.toml` 与 `uv.lock` 尚未包含 Playwright 依赖。
- 当前尚未安装 Playwright Chromium 浏览器运行时；只安装 Python 包不足以启动浏览器。

## 下一步计划

1. 完成阶段四第一课：安装 Playwright 与 Chromium，运行临时启动验证并删除临时脚本。
2. 下一课实现 `core/web_driver.py` 与 pytest 浏览器 fixture，管理浏览器、context 和 page 的生命周期。
3. 随后实现 `pages/base_page.py`，再封装登录页与订单页。

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
- 阶段二第四节课完成：建立 `OrderService`，把鉴权 header 与订单 CRUD 细节集中到服务层；提交为 `1f78b61`。
- 阶段二第五节课完成：把 base_url、客户端、登录用户、token 与订单服务接入 `conftest.py`；学习者确认通过。
- 阶段二第六节课完成：新增 7 条正式鉴权 API 用例并通过专项、全套和 marker 回归。
- 阶段二第七节课完成：新增 9 个订单 API 测试项并完成订单、鉴权、用户隔离验收；提交为 `e2c45f7`。
- 阶段二第八节课完成：实现脱敏后的完整请求响应日志，提交为 `3d32010`；阶段二全部验收通过。
- 阶段三第一节课完成：新增 `pydantic-settings`、PyYAML、类型安全 `Settings` 与 YAML 加载器；学习者确认通过。
- 阶段三第二节课完成：新增 `dev.yaml` 与 `staging.yaml`，提交为 `34f44ef`；学习者确认通过。
- 阶段三第三节课完成：接入 `--env`、`settings` fixture 与配置接线测试；`api_client` 已读取环境的超时和 SSL 配置，提交基线为 `a67c41d`，学习者确认通过。
- 阶段三第四节课完成：新增 `testdata/orders.yaml`、YAML 加载器和 6 项参数化订单用例；学习者确认专项与全套验收通过。
- 阶段三第五节课完成：接入 Allure feature/story/step，自动附加脱敏请求与响应 JSON，并通过 `allure serve` 验收。
- 阶段三第六节课完成：实现按测试隔离的请求历史，在失败时自动附加汇总上下文，学习者确认通过。
- 阶段三总验收完成：学习者确认阶段三正式完成；数据驱动、多环境配置、Allure 报告和失败诊断能力形成闭环。
- 阶段三提交完成：Ruff 检查通过，全部阶段三成果提交为 `355ed4b 完整最终allure报告功能`。
- 阶段四开始：确定使用 Playwright sync API，避免额外引入 pytest-playwright 生命周期层，后续由框架自行实现浏览器 fixture 和页面对象。
