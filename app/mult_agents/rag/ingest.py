import argparse
import logging
import os
import sys
from pathlib import Path

# 先把项目根目录放进 PYTHONPATH，确保可以直接 python app/... 运行。
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_INPUT_PATH = PROJECT_ROOT / "docs"
DEFAULT_EMBEDDING_MODEL = "text-embedding-v1"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将本地文档导入 Milvus 向量库")
    parser.add_argument(
        "--input-path",
        default=str(DEFAULT_INPUT_PATH),
        help="待入库的文件或目录，默认使用项目根目录下的 docs/",
    )
    parser.add_argument(
        "--collection-name",
        default="",
        help="Milvus collection 名称，默认读取 .env/config.json 中的 milvus_collection",
    )
    parser.add_argument(
        "--milvus-host",
        default="",
        help="Milvus 主机地址，默认读取 .env/config.json 中的 milvus_host",
    )
    parser.add_argument(
        "--milvus-port",
        type=int,
        default=0,
        help="Milvus 端口，默认读取 .env/config.json 中的 milvus_port",
    )
    return parser


def _collect_paths(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    patterns = ("*.txt", "*.md", "*.markdown")
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(sorted(input_path.rglob(pattern)))
    return paths


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    # 某些 Windows 代理设置会拦住 tiktoken 首次下载编码文件，这里仅对当前进程绕过代理。
    os.environ.setdefault("NO_PROXY", "*")
    os.environ.setdefault("no_proxy", "*")

    args = _build_parser().parse_args()

    from app.mult_agents.config import AppConfig
    from app.mult_agents.rag.core import RAGConfig, RAGSystem

    config = AppConfig.from_file()

    collection_name = args.collection_name or config.milvus_collection
    milvus_host = args.milvus_host or config.milvus_host
    milvus_port = args.milvus_port or config.milvus_port
    input_path = Path(args.input_path).expanduser()
    if not input_path.is_absolute():
        input_path = (PROJECT_ROOT / input_path).resolve()
    else:
        input_path = input_path.resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"未找到待入库路径: {input_path}")

    paths = _collect_paths(input_path)
    if not paths:
        raise ValueError(f"未找到可入库文件: {input_path}")

    rag_config = RAGConfig(
        milvus_host=milvus_host,
        milvus_port=milvus_port,
        collection_name=collection_name,
        base_url=config.base_url,
        embedding_model=DEFAULT_EMBEDDING_MODEL,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )
    rag = RAGSystem(api_key=config.api_key, config=rag_config)

    total_chunks = rag.ingest_paths(paths)
    print(
        f"入库完成 | 文件数={len(paths)} | chunk数={total_chunks} | "
        f"collection={collection_name} | input={input_path}"
    )


if __name__ == "__main__":
    main()
