"""
线 1 上线冲刺：房源提取 HTTP 服务（AI 应用开发详解教程 第 7 章的"服务化"落地）

架构 B 里的【AI 服务端】：
    Java 后台 ──HTTP──→ 本服务 ──SDK──→ Claude API

跑法：  python -X utf8 -m uvicorn server:app --port 8300
测试：  curl -X POST http://127.0.0.1:8300/extract -H "Content-Type: application/json" \
            -d '{"text":"两室一厅89平朝南月租3200停车方便"}'
"""
import pathlib
import sys

# 把 02-eval-practice-house 加进模块搜索路径，直接复用穿好盔甲的提取器
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "02-eval-practice-house"))

from fastapi import FastAPI
from pydantic import BaseModel
from extractor import extract_listing   # 已带：超时 + 重试 + 限流退避

app = FastAPI(title="房源提取服务", version="1.0")


class ExtractRequest(BaseModel):
    """请求体格式：{"text": "一段房源描述"}——pydantic 在接口边界做参数校验"""
    text: str


@app.get("/")                     # 健康检查：浏览器打开 http://127.0.0.1:8300 就能看到
def health():
    return {"status": "ok", "service": "extract-service", "usage": "POST /extract"}


@app.post("/extract")             # 核心接口：把一段房源描述变成 5 个结构化字段
def extract(req: ExtractRequest):
    try:
        listing = extract_listing(req.text)          # 复用 extractor，业务逻辑零重复
        return {"ok": True, "data": listing.model_dump()}
    except Exception as e:                           # 兜底：服务永不抛堆栈给调用方
        # （到这里说明重试都用尽了——这正是 extractor 里盔甲的"重试用尽向上抛"）
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
