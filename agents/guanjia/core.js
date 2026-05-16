console.log("🔥 guanjia CORE V3 LOADED");

const { detect } = require("./routing");
const { safeDispatch } = require("./safeDispatch");
const { notifyFeishuDM } = require("./notify");
const { agents } = require("./agent");
const { decide } = require("./decider");

// ===== timeout =====
async function withTimeout(promise, ms = 8000) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("timeout")), ms)
    )
  ]);
}

// ===== 执行层 =====
async function runMeta(agentList, task) {
  console.log("🧠 META EXEC:", agentList);

  const results = await Promise.allSettled(
    agentList.map(agent =>
      withTimeout(
        safeDispatch(agent, task, agents[agent])
      )
    )
  );

  return results.map((r, i) => {
    const agent = agentList[i];

    if (r.status === "fulfilled") {
      return {
        agent,
        success: true,
        output: r.value
      };
    } else {
      notifyFeishuDM(agent, task, r.reason.message);

      return {
        agent,
        success: false,
        error: r.reason.message
      };
    }
  });
}

// ===== CHAT =====
async function runChat(task) {
  return `🤖 guanjia：${task}`;
}

// ===== 主流程 =====
async function run(task) {
  console.log("🧠 CORE RUN:", task);

  const decision = await detect(task);

  // 👉 chat
  if (decision.mode === "chat") {
    return await runChat(task);
  }

  // 👉 meta执行
  const rawResults = await runMeta(decision.agents, task);

  // 👉 🔥 二次决策层
  const final = await decide(task, rawResults);

  return final;
}

module.exports = { run };