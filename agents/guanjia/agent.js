console.log("🚨 AGENT.JS ENTRY LOADED");

// ===== agent registry（必须存在）=====

// 每个 agent 必须是 async function

async function suanming(task) {
  return {
    result: `算命结果: ${task}`
  };
}

async function jirou(task) {
  return {
    result: `健身建议: ${task}`
  };
}

async function zhaocai(task) {
  return {
    result: `赚钱策略: ${task}`
  };
}

// ❗核心：必须叫 agents，且 key 要对上规则
const agents = {
  suanming,
  jirou,
  zhaocai
};

module.exports = {
  agents
};