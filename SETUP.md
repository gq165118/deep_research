# DeepResearch 环境搭建说明

这份文档用于从零启动本项目。克隆仓库后，按顺序完成 Docker 服务、后端、RAG 入库和前端启动。

## 1. 前置环境

- Python 3.10 或 3.11
- Node.js 20.19+ 或 22.12+
- Docker Desktop
- AGICTO API Key
- Bocha API Key，可选，用于网络检索

## 2. 启动 Docker 服务

### PostgreSQL

```powershell
docker run -d --name postgres `
  --restart unless-stopped `
  -p 5432:5432 `
  -e POSTGRES_USER=root `
  -e POSTGRES_PASSWORD=YourPostgresPassword `
  -e POSTGRES_DB=deepresearch `
  -v postgres-data:/var/lib/postgresql/data `
  postgres:16
```

### Redis，可选

```powershell
docker run -d --name redis `
  --restart unless-stopped `
  -p 6379:6379 `
  -e REDIS_PASSWORD=YourRedisPassword `
  -v redis-data:/bitnami/redis/data `
  bitnami/redis:latest
```

### Milvus

```powershell
cd docker\milvus
docker compose up -d
cd ..\..
```

Attu 可视化界面默认是：

```text
http://localhost:18000
```

## 3. 配置后端

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

最小配置：

```env
AGICTO_API_KEY=你的真实Key
AGICTO_BASE_URL=https://api.agicto.cn/v1
AGICTO_MODEL=gpt-5.4
ENABLE_MEMORY=false
ENABLE_MILVUS=false
```

启用 PostgreSQL 和 Milvus：

```env
ENABLE_MEMORY=true
SHORT_TERM_BACKEND=postgres
LONG_TERM_BACKEND=postgres
CHECKPOINTER_BACKEND=postgres
ENABLE_MILVUS=true
POSTGRES_DSN=postgresql://root:YourPostgresPassword@127.0.0.1:5432/deepresearch
REDIS_URL=redis://:YourRedisPassword@127.0.0.1:6379/0
MILVUS_HOST=127.0.0.1
MILVUS_PORT=19530
MILVUS_COLLECTION=mult_agent_memory
BOCHA_API_KEY=你的BochaKey
```

## 4. 导入本地知识库

把允许公开或允许用于本地检索的文档放到 `docs/`，然后执行：

```powershell
python .\app\mult_agents\rag\ingest.py
```

默认会读取 `docs/` 下的 `.txt`、`.md`、`.markdown` 文件并写入 Milvus。

## 5. 启动后端

```powershell
uvicorn app.app_main:app --host 127.0.0.1 --port 8000
```

验证地址：

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## 6. 启动前端

新开一个终端：

```powershell
cd front\agent_front
npm install
npm run dev
```

前端默认地址：

```text
http://localhost:5173
```

## 7. CLI 运行

```powershell
python main.py --user-id user03 --thread-id th --once-query "你好，简单介绍一下你自己"
```

## 8. 提交安全

不要提交 `.env`、`.venv/`、`notes/`、`output/`、`node_modules/`、`dist/`、Docker 运行数据目录以及任何真实密钥。
