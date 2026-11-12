# extract-service —— 房源提取 HTTP 服务

> 线 1 上线冲刺的产出：把 `02-eval-practice-house` 的提取器变成一个
> 被其他系统（Java 后台）调用的 HTTP 服务。架构 B 全链路：

```
Java 后台 ──HTTP(8300)──→ 本服务 ──SDK──→ Claude API（中转站）
  ↑ resilience4j 思路         ↑ 盔甲：超时+重试+限流退避
  java-demo/JavaClientDemo.java（JDK8 零依赖演示版）
```

## 怎么跑（两步）

```bash
# ① 启动 AI 服务（终端 1）
cd D:\studyAi\studyai\06-extract-service
python -X utf8 -m uvicorn server:app --port 8300

# ② 编译并运行 Java 调用方（终端 2，需 JDK 11+；本机用 E:\env\jdk-17.0.20.1+1）
cd java-demo
"/e/env/jdk-17.0.20.1+1/bin/javac" -encoding UTF-8 JavaClientDemo.java
"/e/env/jdk-17.0.20.1+1/bin/java" -Dfile.encoding=UTF-8 JavaClientDemo
```

## 接口说明

| 接口 | 方法 | 用途 |
|---|---|---|
| `/` | GET | 健康检查（浏览器直接打开即可） |
| `/extract` | POST | 请求体 `{"text": "一段房源描述"}`，返回 5 个结构化字段 |

返回格式：`{"ok": true, "data": {"layout": "2室1厅", "area": 89, "price": 3200,
"orientation": "南", "parking": true}}`；失败时 `{"ok": false, "error": "..."}`。

## 盔甲分布（每一跳都有）

| 位置 | 盔甲 | 实现 |
|---|---|---|
| extractor → Claude API | 超时 30s + 重试×3（指数退避）+ 429 读 retry-after | `extractor.py` 的 `call_with_retry` |
| 本服务兜底 | 重试用尽也不抛堆栈，返回 `{"ok":false}` | `server.py` 的 try/except |
| Java → 本服务 | 超时 5s/32s + 重试×3 + 降级人话文案 | `JavaClientDemo.java` |

**规矩**：同一个失败只在一层重试（AI 服务层管对 Claude 的重试；Java 层管对服务的重试）。

## 边界（当前版本不做的）

- 单进程、无并发压测（个人学习级）；生产要加 uvicorn workers + 反向代理
- 无鉴权——只监听本机 127.0.0.1，不要暴露公网
- 朝向字段准确率 ~40%（基础模型没修提示词，属 MISSIONS 第 2 关的活，与本服务无关）

## 工作参考：Spring Boot 生产版（伪代码）

```java
@Retry(name = "aiApi", fallbackMethod = "fallback")   // 重试+兜底
@TimeLimiter(name = "aiApi")                          // 超时
@RateLimiter(name = "aiApi")                          // 限流
public String callAi(String text) {
    return restTemplate.postForObject(SERVICE + "/extract", req, String.class);
}
public String fallback(String text, Throwable t) {
    return "{\"ok\":false,\"error\":\"AI 服务暂不可用\"}";
}
```
