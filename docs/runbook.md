# 自动化测试运行手册

## 1. 适用范围

本手册用于运行、排查和维护订单管理系统的 UI/API 自动化测试框架。

相关目录：

- `app/`：FastAPI + SQLite + 原生 HTML/JS 被测系统。
- `automation/`：独立的 uv pytest 自动化项目。
- `docs/`：学习路径、项目记忆、运行手册和协作规范。

所有自动化命令默认在对应目录执行：

- 被测系统命令：项目根目录。
- pytest 与报告分析命令：`automation/`。
- Docker Compose 命令：项目根目录。

## 2. 安全边界

### 2.1 环境分级

| 环境 | 默认执行档位 | 允许档位 | 写操作 | 用途 |
|---|---|---|---|---|
| `dev` | `full` | `full`、`regression`、`smoke` | 允许 | 本地开发与完整回归 |
| `staging` | `regression` | `regression`、`smoke` | 按预发数据策略 | 预发回归与巡检 |
| `prod` | `smoke` | 仅 `smoke` | 禁止 | 只读巡检占位配置 |

生产配置默认开启：

```yaml
read_only: true
```

`APIClient` 在请求发出前阻止：

- `POST`
- `PUT`
- `PATCH`
- `DELETE`

允许：

- `GET`
- `HEAD`
- `OPTIONS`

不得为了让测试通过而关闭生产只读保护。

### 2.2 当前生产配置说明

`automation/config/prod.yaml` 当前使用：

```text
https://prod.example.invalid
```

这是不可解析的占位域名，不代表已经接入真实生产系统。

接入真实生产前必须完成：

1. 只读身份和最小权限。
2. 独立 secret 管理。
3. 仅启用只读 GET 巡检。
4. 限流、熔断和告警阈值评审。
5. 产品、运维和测试负责人共同确认。

### 2.3 测试数据

- 测试用户和订单由 Faker 动态生成。
- 本地测试结束后通过 `DBClient` 清理用户、session 和订单。
- 不允许在生产环境创建测试用户或订单。
- 不得提交 `.env`、数据库、token、截图、报告和日志。

## 3. 环境准备

### 3.1 本地被测系统

项目根目录：

```powershell
cd E:\python-pytest-ci-cd-ui-api
.\start.ps1
```

访问：

- 前端：<http://127.0.0.1:8000/>
- Swagger：<http://127.0.0.1:8000/docs>
- OpenAPI：<http://127.0.0.1:8000/openapi.json>

健康检查：

```powershell
Invoke-WebRequest http://127.0.0.1:8000/openapi.json |
    Select-Object StatusCode
```

预期：

```text
StatusCode
----------
       200
```

PowerShell 禁止执行脚本时，当前窗口临时处理：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start.ps1
```

### 3.2 自动化依赖

```powershell
cd E:\python-pytest-ci-cd-ui-api\automation
uv sync --frozen
uv run playwright install chromium
```

依赖锁定检查：

```powershell
uv lock --check
```

### 3.3 配置优先级

配置来自：

1. `config/<env>.yaml`
2. `AUTOMATION_*` 环境变量覆盖

常用环境变量：

```text
AUTOMATION_ENVIRONMENT
AUTOMATION_BASE_URL
AUTOMATION_TIMEOUT_SECONDS
AUTOMATION_VERIFY_SSL
AUTOMATION_READ_ONLY
AUTOMATION_TRAFFIC_TAG
AUTOMATION_DATABASE_PATH
AUTOMATION_MIN_REQUEST_INTERVAL_SECONDS
AUTOMATION_CIRCUIT_FAILURE_THRESHOLD
AUTOMATION_CIRCUIT_RECOVERY_SECONDS
```

## 4. 常用运行命令

### 4.1 本地全量

```powershell
cd E:\python-pytest-ci-cd-ui-api\automation
uv run pytest -v --env=dev
```

当前完整基线：

```text
93 passed
```

### 4.2 API 回归

```powershell
uv run pytest tests/api -v --env=dev
```

### 4.3 UI 回归

```powershell
uv run pytest tests/ui -v --env=dev
```

### 4.4 混合 E2E

```powershell
uv run pytest tests/e2e/test_user_journey.py -v --env=dev
```

预期：

```text
1 passed
```

### 4.5 serial 通道

```powershell
uv run pytest -m serial -v --env=dev
```

预期：

```text
2 passed
```

### 4.6 smoke 档位

```powershell
uv run pytest --env=dev --suite=smoke -v
```

### 4.7 生产只读 smoke

```powershell
uv run pytest --env=prod
```

预期：

```text
automation environment: prod
automation suite: smoke
6 passed
```

生产 smoke 当前不访问真实生产系统。

尝试生产回归必须被拒绝：

```powershell
uv run pytest --env=prod --suite=regression
```

预期报错：

```text
prod 环境不允许 --suite=regression
```

## 5. Docker 运行

项目根目录：

```powershell
cd E:\python-pytest-ci-cd-ui-api

docker compose up --build `
  --abort-on-container-exit `
  --exit-code-from automation
```

三个通道预期：

```text
90 passed
2 passed
1 passed
```

合计：

```text
93 passed
```

检查容器：

```powershell
docker compose ps
```

查看日志：

```powershell
docker compose logs --no-color app
docker compose logs --no-color automation
```

停止容器：

```powershell
docker compose down
```

不要随意执行：

```text
docker compose down -v
```

`-v` 会删除 Compose 数据卷。

## 6. 报告与产物

主要位置：

```text
automation/reports/
automation/screenshots/
```

关键文件：

| 文件 | 用途 |
|---|---|
| `report.html` | 本地完整 HTML 报告 |
| `report-parallel.html` | Docker 并行通道报告 |
| `report-serial.html` | Docker serial 通道报告 |
| `report-smoke.html` | Docker smoke 通道报告 |
| `docker-allure/` | Docker 全量 Allure 原始结果 |
| `flaky-summary.json` | 本地 flaky 汇总 |
| `flaky-parallel.json` | 并行通道 flaky 汇总 |
| `flaky-serial.json` | serial 通道 flaky 汇总 |
| `flaky-smoke.json` | smoke 通道 flaky 汇总 |
| `analytics/dashboard.json` | 当前失败聚类与趋势 |
| `analytics/history.json` | 跨运行历史 |
| `analytics/summary.md` | Actions Job Summary |
| `docker-compose.log` | Compose 运行日志 |

### 6.1 查看 Allure

本地：

```powershell
cd E:\python-pytest-ci-cd-ui-api\automation
allure serve .\reports\docker-allure
```

GitHub Actions 推送主分支后会发布静态 Allure。实际地址以 `deploy-pages` 步骤输出的 `page_url` 为准。

通常仓库 Pages 地址为：

```text
https://johnnydark110-cpu.github.io/python-pytest-ci-cd-ui-api/
```

不应每次下载 artifact 后手工启动 Allure；Pages 是常规查看入口。

### 6.2 生成失败聚类

本地完整结果：

```powershell
cd E:\python-pytest-ci-cd-ui-api\automation

uv run python .\report_analytics.py `
    --report-file .\reports\flaky-summary.json `
    --history .\reports\analytics\history.json `
    --output .\reports\analytics\dashboard.json `
    --summary-md .\reports\analytics\summary.md `
    --run-id local `
    --commit local `
    --branch local
```

Docker 三通道结果：

```powershell
uv run python .\report_analytics.py `
    --report-dir .\reports `
    --history .\reports\analytics\history.json `
    --output .\reports\analytics\dashboard.json `
    --summary-md .\reports\analytics\summary.md `
    --run-id docker-local `
    --commit local `
    --branch local
```

## 7. GitHub Actions

工作流：

```text
.github/workflows/ci.yml
```

触发条件：

- push 到 `master` 或 `main`
- pull request
- 手工 `workflow_dispatch`

主要阶段：

1. Ruff 和差异检查。
2. Docker Compose 配置校验。
3. 构建 app 与 automation 镜像。
4. 启动被测系统。
5. 三通道运行测试。
6. 生成失败聚类与趋势。
7. 上传 artifacts。
8. Slack 失败通知。
9. 生成 Allure Pages 报告。

查看入口：

```text
GitHub 仓库 → Actions → Automation Tests
```

主分支运行还会在 Job Summary 中显示：

- 测试结果。
- flaky 数量。
- 失败类别。
- 最近趋势。

## 8. trace_id 与日志

每条测试自动生成唯一 `trace_id`。

请求头：

```text
X-Trace-ID: <32位 trace_id>
X-Traffic-Tag: automation.<env>
```

日志格式：

```text
2026-11-23 12:00:00 | INFO | trace=<trace_id> | automation.core.api_client | ...
```

定位失败时：

1. 从 pytest 日志或 Allure 获取 trace_id。
2. 搜索相同 trace_id。
3. 对照 Allure 请求、响应和失败上下文。
4. 检查请求头中的流量标签。

## 9. 限流与熔断

每个 APIClient worker 独立生效。

配置：

| 环境 | 最小间隔 | 熔断阈值 | 恢复窗口 |
|---|---:|---:|---:|
| dev | 0 秒 | 5 | 5 秒 |
| staging | 0.2 秒 | 3 | 30 秒 |
| prod | 1 秒 | 3 | 60 秒 |

只有传输失败计入熔断：

- 网络拒绝
- DNS 错误
- 代理错误
- 连接超时

HTTP 4xx/5xx 不计入熔断，因为服务端已完成 HTTP 响应。

出现 `CircuitOpenError` 时：

1. 不要立刻关闭熔断。
2. 检查 app、网络、DNS 和代理。
3. 等待恢复窗口。
4. 修复环境后重新运行。

## 10. 失败分诊流程

### 10.1 第一步：停止盲目重跑

连续重跑会放大环境故障。

先检查：

- trace_id
- 失败分类
- Allure 请求响应
- app 日志
- 最近提交
- CI artifact

### 10.2 分类处理

| 分类 | 优先检查 | 处理方式 |
|---|---|---|
| `environment` | app、网络、DNS、代理、熔断 | 恢复环境后有限重试 |
| `configuration` | env、suite、read_only、数据库路径 | 修正配置，不违规绕过 |
| `product_assertion` | 状态码、字段、页面行为、契约 | 对比产品预期并建缺陷 issue |
| `framework_or_test` | 堆栈、fixture、页面对象、导入 | 修复框架或测试代码 |
| `unknown` | 完整 trace 和日志 | 人工归类并补充规则 |

### 10.3 环境故障

```text
分类：environment
处理：检查服务健康、网络和日志
重试：仅允许 APITransportError 的有限重试
禁止：把环境故障长期标记成 known_flaky
```

### 10.4 产品断言失败

`AssertionError` 不自动等于产品缺陷，可能原因：

- 产品行为确实变化。
- JSON Schema 或测试期望过期。
- 页面定位或等待条件错误。
- 测试数据不满足前置条件。

必须对比产品和测试双方后创建 issue。

### 10.5 框架故障

示例：

- `NameError`
- `TypeError`
- `AttributeError`
- fixture 顺序错误
- 页面对象定位失效

此类失败应修复框架，不应增加重试。

## 11. known_flaky 管理

登记示例：

```python
@pytest.mark.known_flaky(
    issue="ISSUE-123",
    owner="qa-team",
    expires="2026-12-31",
    reason="等待订单索引修复",
)
def test_order_index_eventually_visible() -> None: ...
```

规则：

- 四个字段必填。
- 日期格式为 `YYYY-MM-DD`。
- 过期后 pytest 收集阶段失败。
- 必须关联真实 issue。
- 必须有明确 owner。
- 不允许无期限重试。
- 环境故障恢复后应删除 marker，而不是延长期限。

## 12. 事故处理

### 12.1 本地服务不可用

```powershell
Invoke-WebRequest http://127.0.0.1:8000/openapi.json
```

检查终端或容器日志，重新启动 `start.ps1`。

### 12.2 Docker 失败

```powershell
docker compose ps
docker compose logs --no-color app
docker compose logs --no-color automation
docker compose config
```

### 12.3 CI 失败

检查顺序：

1. Ruff。
2. Compose config。
3. 镜像构建。
4. app healthcheck。
5. parallel、serial、smoke 三通道。
6. analytics。
7. artifacts 和 Pages。

## 13. 发布前检查清单

- [ ] `master` 工作区干净。
- [ ] `ruff check .` 通过。
- [ ] `git diff --check` 通过。
- [ ] `uv lock --check` 通过。
- [ ] 本地 93 passed。
- [ ] Docker 90 + 2 + 1 通过。
- [ ] E2E 连续运行稳定。
- [ ] 测试数据清理前后一致。
- [ ] flaky `known_flaky` 未过期。
- [ ] CI 全绿。
- [ ] Allure Pages 可访问。
- [ ] analytics Job Summary 可查看。
- [ ] 没有提交报告、截图、数据库或 secret。

## 14. 维护节奏

### 每次提交

- 运行相关专项测试。
- 更新项目记忆。
- 检查 diff。

### 每次合并主分支

- 检查 CI。
- 查看 flaky 和失败聚类。
- 查看趋势是否恶化。

### 每周

- 清理过期 known_flaky。
- 检查失败分类趋势。
- 检查长期失败模块。

### 每月

- 评审稳定性和运行时长。
- 更新依赖锁。
- 审查生产巡检白名单。
- 复盘事故与回滚流程。
