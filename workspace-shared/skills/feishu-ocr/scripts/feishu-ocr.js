/**
 * 飞书 OCR 工具
 * 使用飞书开放平台 OCR API 识别图片和 PDF 中的文字
 */

const Lark = require("@larksuiteoapi/node-sdk");
const { Domain } = Lark;
const fs = require("fs");
const https = require("https");
const path = require("path");

// 从环境变量获取飞书配置
const FEISHU_APP_ID = process.env.FEISHU_APP_ID || "cli_a92fe3f3ef629cd4";
const FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET || "HyBdu9BiY4MvDWI97wrzpdrQlqFD407I";

// 创建飞书客户端
const client = new Lark.Client({
  appId: FEISHU_APP_ID,
  appSecret: FEISHU_APP_SECRET,
  appType: Lark.AppType.SelfBuild,
  domain: Domain.Feishu,
  disableTokenCache: false,
});

// 获取 tenant_access_token (带缓存)
let cachedToken = null;
let tokenExpireTime = 0;

async function getTenantAccessToken() {
  // 检查缓存
  if (cachedToken && Date.now() < tokenExpireTime - 60000) {
    return cachedToken;
  }

  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      app_id: FEISHU_APP_ID,
      app_secret: FEISHU_APP_SECRET,
    });

    const options = {
      hostname: "open.feishu.cn",
      path: "/open-apis/auth/v3/tenant_access_token/internal",
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Content-Length": Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0 && result.tenant_access_token) {
            cachedToken = result.tenant_access_token;
            tokenExpireTime = Date.now() + result.expire * 1000;
            resolve(result.tenant_access_token);
          } else {
            reject(new Error(`Failed to get token: ${result.msg} (code: ${result.code})`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on("error", reject);
    req.write(postData);
    req.end();
  });
}

// 通过飞书 SDK 识别图片 (本地文件)
async function ocrFromFile(filePath) {
  try {
    const response = await client.optical_char_recognition.image.basicRecognize({
      image: fs.createReadStream(filePath),
    });

    if (response.data?.code) {
      throw new Error(`OCR failed: ${response.data.msg} (code: ${response.data.code})`);
    }

    // 提取文字
    const texts = response.data?.data?.items?.map((item) => item.text).join("\n") || "";
    return texts;
  } catch (error) {
    // 如果是频率限制，等一会重试
    if (error.response?.data?.code === 99991400) {
      console.error("Frequency limit hit, waiting...");
      await new Promise((resolve) => setTimeout(resolve, 5000));
      const response = await client.optical_char_recognition.image.basicRecognize({
        image: fs.createReadStream(filePath),
      });
      
      if (response.data?.code) {
        throw new Error(`OCR failed: ${response.data.msg} (code: ${response.data.code})`);
      }
      
      const texts = response.data?.data?.items?.map((item) => item.text).join("\n") || "";
      return texts;
    }
    throw error;
  }
}

// 通过 URL 识别图片
async function ocrFromUrl(imageUrl) {
  const response = await client.optical_char_recognition.image.basicRecognize({
    image_url: imageUrl,
  });

  if (response.data?.code) {
    throw new Error(`OCR failed: ${response.data.msg} (code: ${response.data.code})`);
  }

  const texts = response.data?.data?.items?.map((item) => item.text).join("\n") || "";
  return texts;
}

// 通过 URL 识别 PDF (需要先把 PDF 上传到飞书云盘获取 URL，或者使用 file_url)
async function ocrFileFromUrl(fileUrl) {
  // 飞书 OCR 支持 file_url，需要先获取一个公开的 PDF URL
  // 这里可以配合飞书云盘上传功能使用
  const token = await getTenantAccessToken();

  const fetch = require("node-fetch");
  const response = await fetch(
    `https://open.feishu.cn/open-apis/ocr/v1/file?file_url=${encodeURIComponent(fileUrl)}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json; charset=utf-8",
      },
    }
  );

  const data = await response.json();

  if (data.code) {
    throw new Error(`OCR failed: ${data.msg} (code: ${data.code})`);
  }

  // 提取文字
  const texts = data.data?.items?.map((item) => item.text).join("\n") || "";
  return texts;
}

// 主函数
async function main() {
  const action = process.argv[2];
  const param = process.argv[3];

  try {
    let result;
    switch (action) {
      case "image_url":
        result = await ocrFromUrl(param);
        break;
      case "image_file":
        result = await ocrFromFile(param);
        break;
      case "file_url":
        result = await ocrFileFromUrl(param);
        break;
      default:
        console.error("Usage:");
        console.error("  node feishu-ocr.js image_url <url>");
        console.error("  node feishu-ocr.js image_file <file_path>");
        console.error("  node feishu-ocr.js file_url <url>");
        process.exit(1);
    }

    console.log(result || "(未识别到文字)");
  } catch (error) {
    console.error("Error:", error.message);
    process.exit(1);
  }
}

main();
