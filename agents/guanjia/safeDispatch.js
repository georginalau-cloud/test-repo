const { notifyFeishuDM } = require("./notify");

async function safeDispatch(agentName, task, agentFn) {
  const TIMEOUT = 3000;
  const RETRY = 1;

  let attempt = 0;

  while (attempt <= RETRY) {
    try {
      const result = await Promise.race([
        agentFn(task),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("timeout")), TIMEOUT)
        )
      ]);

      return {
        agent: agentName,
        success: true,
        data: result
      };

    } catch (err) {
      attempt++;

      console.log(`❌ ${agentName} 失败:`, err.message);

      if (attempt <= RETRY) {
        console.log(`🔁 重试 ${agentName}...`);
        continue;
      }

      // 🚨 非阻塞告警（关键修复点）
      notifyFeishuDM(agentName, task, err.message)
        .catch(e => console.error("notify error:", e));

      // ✅ 结构化返回（给 decider 用）
      return {
        agent: agentName,
        success: false,
        error: err.message
      };
    }
  }
}

module.exports = { safeDispatch };