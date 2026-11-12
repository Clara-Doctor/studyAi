import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * 线 1 上线冲刺：Java 调用方演示（架构 B 的【Java 后台】这一跳）
 *
 * 要求 JDK 11+（本机位置：C:\Program Files\Eclipse Adoptium\jdk-11.0.31.11-hotspot）
 * 用 JDK 11 的标准 HttpClient——生产代码里这个类就是 restful 客户端的底层。
 * 演示生产盔甲三件套的 Java 版：超时 / 重试（指数退避）/ 降级兜底。
 *
 * 编译：javac -encoding UTF-8 JavaClientDemo.java
 * 运行：java -Dfile.encoding=UTF-8 JavaClientDemo     （前提：Python 服务已在 8300 端口跑着）
 *
 * 【工作参考】真实 Spring Boot 项目请用 resilience4j 替代手写重试：
 *   @Retry(name = "aiApi", fallbackMethod = "fallback")
 *   @TimeLimiter(name = "aiApi")
 *   public String callAi(String text) { ... }        // 三个注解 = 本文件的三个方法
 */
public class JavaClientDemo {

    static final String SERVICE = "http://127.0.0.1:8300";

    /** 盔甲①（连接层）：共享一个 HttpClient，连接超时 5 秒 */
    static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    public static void main(String[] args) {
        String[] samples = {
                "两室一厅89平朝南月租3200停车方便",
                "南北通透三居室145平精装修租金9000元每月",
                "小区环境好拎包入住"      // 全字段缺失用例：验证 null 纪律穿透整条链路
        };
        for (String text : samples) {
            System.out.println("输入: " + text);
            System.out.println("结果: " + postWithRetry(text));
            System.out.println("--------------------------------------------------");
        }
    }

    /** 盔甲②：重试（指数退避 1s→2s→4s）+ 盔甲③：降级兜底 */
    static String postWithRetry(String text) {
        int maxRetries = 3;
        long baseDelay = 1000;
        String body = "{\"text\": \"" + text + "\"}";
        for (int attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                return post(body);
            } catch (Retryable e) {                       // 可重试的失败（超时/断连/429/5xx）
                if (attempt == maxRetries) {
                    // 盔甲③降级：重试用尽也不抛异常堆栈给用户，给一句人话
                    return "{\"ok\":false,\"error\":\"服务暂不可用，请稍后再试\"}";
                }
                long wait = baseDelay * (1L << attempt);  // 1000 → 2000 → 4000 ms
                System.out.println("[重试] " + e.getMessage() + "，" + wait + "ms 后重试…");
                try { Thread.sleep(wait); } catch (InterruptedException ignored) { }
            }
        }
        return "{\"ok\":false,\"error\":\"unreachable\"}";   // 理论到不了这里
    }

    /** 盔甲①（请求层）：读超时 32s（略大于 AI 服务内部的 30s）。错误分类：该重试的抛 Retryable */
    static String post(String body) throws Retryable {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(SERVICE + "/extract"))
                .timeout(Duration.ofSeconds(32))              // 请求级超时
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        HttpResponse<String> resp;
        try {
            resp = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (java.io.IOException | InterruptedException e) {
            throw new Retryable(e.getClass().getSimpleName());   // 网络问题：可重试
        }
        int code = resp.statusCode();
        if (code == 429 || code >= 500) throw new Retryable("HTTP " + code);      // 对方问题：重试
        if (code >= 400) return "请求被拒绝（HTTP " + code + "，不重试）：" + resp.body(); // 自己问题：不重试
        return resp.body();
    }

    /** 标记"这个失败值得重试"的自定义异常（同文件配套类） */
    static class Retryable extends Exception {
        Retryable(String msg) { super(msg); }
    }
}
