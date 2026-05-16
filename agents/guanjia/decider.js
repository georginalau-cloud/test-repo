async function callModel(prompt) {
  // 👉 替换为真实模型
  return "";
}

async function decide(task, results) {
  const prompt = `
你是 guanjia 的最终决策层。

用户问题：
${task}

agent返回：
${JSON.stringify(results, null, 2)}

你的任务：
1. 判断哪些结果有效
2. 忽略失败或低质量
3. 融合多个agent结果
4. 给出最终答案

要求：
- 简洁
- 不要提及agent
- 直接回答用户

输出纯文本
`;

  try {
    const res = await callModel(prompt);

    if (!res) throw new Error("empty");

    return res;

  } catch (e) {
    // 👉 fallback：简单拼接
    return results.map(r =>
      r.success
        ? `✅ ${r.agent}：${r.output}`
        : `❌ ${r.agent}：${r.error}`
    ).join("\n\n");
  }
}

module.exports = { decide };