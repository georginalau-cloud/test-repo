const https = require("https");

const FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f1863ec4-9f48-491a-9519-28a1660339b8";

function notifyFeishuDM(agent, task, error) {
  // ✅ 防误触（必须有 error 才发）
  if (!error) return Promise.resolve();

  const payload = JSON.stringify({
    msg_type: "text",
    content: {
      text: `🚨 guanjia告警
agent: ${agent}
task: ${task}
error: ${error}`
    }
  });

  return new Promise((resolve) => {
    try {
      const url = new URL(FEISHU_WEBHOOK);

      const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      };

      const req = https.request(options, (res) => {
        // ✅ 不关心返回结果，不影响主流程
        resolve();
      });

      req.on("error", (err) => {
        console.error("notify failed:", err.message);
        resolve(); // ✅ 吞掉错误
      });

      req.write(payload);
      req.end();

    } catch (e) {
      console.error("notify exception:", e.message);
      resolve(); // ✅ 保证不抛出
    }
  });
}

module.exports = { notifyFeishuDM };