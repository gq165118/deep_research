# DeepResearch

基于 LangGraph 的企业级多智能体深度研究助手。系统会先判断用户问题是否需要深度研究，再通过 Planner 拆解任务，由 Web Scout 和 Local Scout 并行检索外网与本地知识库，交给 Evidence Judge 做证据审计，最后由 Analyst 判断是否需要补搜，并由 Writer 生成带引用来源的深度研报。

一句话总结：

> 可规划、可检索、可审计、可补搜、可溯源的 AI 研究工作流。

## 功能特性

- 意图分流：闲聊走 Direct Responder 秒回，调研类问题走完整研究链路。
- 双源并行检索：Web Scout 走 Bocha API，Local Scout 走 Milvus 本地知识库，两路并行。
- 证据审计：Evidence Judge 打分、去重、标注冲突，输出统一 source_index。
- 迭代补搜：Analyst 发现缺口 → Reflect 生成新查询 → 重新检索，最大迭代次数可控。
- 引用校验：Writer 输出后正则校验 source_id 合法性，非法引用自动移除。
- 两层记忆：短期会话记忆（PostgreSQL checkpointer）+ 长期语义记忆（Milvus 向量 + PostgreSQL 画像）。
- 三种入口：CLI、FastAPI、Vue3 前端。

## 技术栈

- 编排：LangGraph、LangChain
- 后端：FastAPI、Uvicorn
- 模型：AGICTO OpenAI 兼容接口（默认 `gpt-5.4`）
- 向量库：Milvus（可选）
- 关系库：PostgreSQL（短期/长期记忆 + checkpointer）
- 缓存：Redis（可选）
- 前端：Vue 3 + Vite + TypeScript

## 目录结构

```text
deep_research/
├── app/
│   ├── app_main.py             # FastAPI 入口
│   ├── backend/                # API 层：路由、Schema、Service
│   └── mult_agents/            # 多智能体核心
│       ├── graph.py            # LangGraph 工作流定义
│       ├── nodes.py            # 各节点执行逻辑
│       ├── prompts.py          # 各 Agent 提示词
│       ├── state.py            # ResearchState 定义
│       ├── tools.py            # Bocha / 通用工具
│       ├── config.py           # AppConfig
│       ├── main.py             # CLI 入口和 Agent 构建
│       ├── memory/             # 短期 + 长期记忆
│       └── rag/                # RAG 核心与入库脚本
├── front/agent_front/          # Vue 3 前端
├── docs/                       # 本地知识库原文
├── SETUP.md                    # 详细安装与运行说明
├── main.py                     # CLI 启动入口
├── config.json                 # 默认配置
├── requirements.txt            # Python 依赖
└── .env.example                # 环境变量模板
```

## 环境要求

- Python 3.10 或 3.11
- Node.js ≥ 20.19 或 ≥ 22.12（仅运行前端时需要）
- Docker / Docker Desktop（运行 PostgreSQL、Milvus 时需要）
- AGICTO API Key（必需）
- Bocha API Key（启用网络检索时需要）

详细的安装与部署步骤见 [SETUP.md](SETUP.md)。

## 快速开始

### 1. 克隆并进入仓库

```bash
git clone <仓库地址> deep_research
cd deep_research
```

### 2. 创建虚拟环境并安装依赖

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```powershell
Copy-Item .env.example .env
```

最小可跑配置：

```env
AGICTO_API_KEY=你的真实Key
AGICTO_BASE_URL=https://api.agicto.cn/v1
AGICTO_MODEL=gpt-5.4
ENABLE_MEMORY=false
ENABLE_MILVUS=false
```

完整配置项见 [.env.example](.env.example)。

### 4. 启动后端

```powershell
python -m app.app_main
```

或者：

```powershell
uvicorn app.app_main:app --host 127.0.0.1 --port 8000
```

后端默认监听 `http://127.0.0.1:8000`。可以通过以下地址验证：

- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) — 健康检查
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — Swagger UI

> 访问根路径 `/` 会返回 `{"detail":"Not Found"}`，这是正常现象，项目没有注册根路由。

### 5. 启动前端（可选）

新开一个终端：

```powershell
cd front\agent_front
npm install
npm run dev
```

前端默认监听 `http://localhost:5173`。Vite 已配置代理，`/api` 和 `/health` 会转发到后端 8000 端口，前端代码里不用硬编码后端地址。

### 6. CLI 模式（可选）

不启动后端也能跑：

```powershell
python main.py --user-id user03 --thread-id th --once-query "你好，简单介绍一下你自己"
```

交互模式：

```powershell
python main.py --user-id user03 --thread-id th
```

## 完整能力启用

想开启 PostgreSQL 记忆、Milvus 向量检索和 Bocha 网络检索，按以下顺序配置：

1. 用 Docker 启动 PostgreSQL 和 Milvus。
2. 填 `POSTGRES_DSN`、`MILVUS_HOST`、`BOCHA_API_KEY`。
3. 将 `ENABLE_MEMORY` 和 `ENABLE_MILVUS` 改为 `true`。
4. 运行 `python app/mult_agents/rag/ingest.py` 把 `docs/` 下的资料入库。
5. 重启后端。

详细操作步骤见 [SETUP.md](SETUP.md)。

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查 |
| POST | `/api/v1/research/run` | 同步执行研究，返回最终报告 |
| POST | `/api/v1/research/stream` | 流式推送节点状态和最终报告（SSE）|

请求示例：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/research/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "调研一下2026年AI Agent平台市场",
    "user_id": "user01",
    "thread_id": "thread01",
    "tenant_id": "default_tenant"
  }'
```

更多参数和返回字段见 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)。

## 常见问题

- **`ModuleNotFoundError: No module named 'mult_agents'`**：`mult_agents` 位于 `app/` 下，需要把 `app/` 加入 `sys.path`。`main.py` 和 [app/app_main.py](app/app_main.py) 已内置 `_bootstrap()`，确保从这两个入口启动。
- **后端根路径返回 `Not Found`**：正常现象，访问 `/health` 或 `/docs` 即可。
- **前端 `ERR_CONNECTION_REFUSED`**：前端开发服务器没启动，参考第 5 步。
- **`cd` 失败后 `npm install` 报 ENOENT**：确认目录名是 `deep_research`，不是 `dep_research`。
- **PostgreSQL / Milvus 连接失败**：检查容器状态，核对 `.env` 中的 DSN 和主机端口。

其他问题参考 [SETUP.md](SETUP.md)。


## 安全提示

- `.env` 含真实密钥，不要提交或分享。
- 公网部署时不要让 `/docs` 暴露在无鉴权环境。
- 本地知识库入库前请确认数据可外发，尤其是接入外部模型时。
