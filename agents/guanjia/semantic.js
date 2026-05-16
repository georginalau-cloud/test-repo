
console.log("✅ semantic loaded");

const ALL_AGENTS = ["zhaocai", "jirou", "suanming"];

// ⚠️ 当前不使用模型，仅用于验证调度链
async function callModel(prompt) {
  return "";
}

async function semanticDetect(task) {
  // ✅ 强制日志（必须出现）
  console.log("🧪 [FORCE META TEST] task:", task);

  // ✅ 强制进入 meta 调度
  return {
    mode: "meta",
    agents: ["guanjia"]
  };
}

module.exports = { semanticDetect };

