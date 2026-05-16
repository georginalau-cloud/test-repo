const { semanticDetect } = require("./semantic");

async function detect(task) {
  console.log("🔍 routing (LLM):", task);

  const res = await semanticDetect(task);

  return res;
}

module.exports = { detect };