# 项目记忆

## 当前状态

- 当前阶段：阶段 0（项目准备与被测系统搭建）
- 更新时间：2026-11-13
- 状态：进行中（等待学习者完成浏览器验收）

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
- git 仓库已初始化并完成首次提交（提交信息：`接触骨架搭建`）。

## 待办

- 学习者启动系统，在浏览器和接口文档中各验证一遍。
- 阶段 0 验收通过后进入阶段一。

## 项目结构快照

- `AGENTS.md`：AI 教学规范与项目约束。
- `app/backend/`：FastAPI 后端。
- `app/frontend/`：前端静态资源。
- `automation/`：自动化框架（阶段一起填充）。
- `docs/learning-path.md`、`docs/project-memory.md`：教学文档。

## 已知问题

- 无。

## 下一步计划

1. 学习者按阶段 0 验收清单自查。
2. 确认通过后，进入阶段一：初始化 `automation/` 环境与工具链。