"""
公共盔甲模块：call_with_retry（关7 凭记忆重写版）
对比 extractor.py 里那份：逻辑相同（错误分类 + 指数退避 + retry-after），写法更紧凑。
放公共模块的原因（DRY 原则）：同一逻辑写两份，将来改 bug 必漏一处。
"""
import time
import anthropic


def call_with_retry(make_request, max_retries=3, base_delay=1.0):
    """把一次 API 调用包上"失败自动重试"外壳。
    可重试：429 / 5xx / 超时 / 断连（对方或网络的问题）
    不重试：4xx 参数错（自己的问题，重试一万次也是错）"""
    last = None
    for attempt in range(max_retries + 1):
        try:
            return make_request()
        except anthropic.RateLimitError as e:
            wait = float(e.response.headers.get("retry-after", base_delay * 2 ** attempt))
        except anthropic.APIStatusError as e:
            if e.status_code < 500:
                raise
            wait = base_delay * 2 ** attempt
        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as e:
            last = e
            wait = base_delay * 2 ** attempt
        if attempt == max_retries:
            raise
        print(f"[重试] {type(last).__name__ if last else '限流'}，{wait:.1f}s 后第 {attempt + 1} 次重试…")
        time.sleep(wait)
