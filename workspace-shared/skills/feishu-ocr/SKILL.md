---
name: feishu-ocr
description: |
  飞书 OCR 文字识别。使用飞书开放平台 API 识别图片或 PDF 中的文字，免费且不限次数。
  当用户要求识别图片/截图/PDF中的文字、提取文字内容时触发。
---

# 飞书 OCR 技能 📷

## 简介

使用飞书开放平台 OCR API 识别图片或 PDF 中的文字。**完全免费，不限次数**。

## 使用方式

### 识别图片中的文字

用户提供图片（截图、照片等），提取其中的文字：

1. 如果图片在本地 → 直接调用 `feishu_ocr` action="image_file"
2. 如果图片是 URL → 调用 `feishu_ocr` action="image_url"
3. 如果图片在飞书消息中 → 先用 feishu_chat 的 download_image 下载，再 OCR

### 识别 PDF 中的文字

对于 PDF 文件，需要先提取图片或使用飞书云盘上传后 OCR：

1. 方案A：将 PDF 页转为图片，再 OCR
2. 方案B：上传到飞书云盘，用 `action: "file"` 识别

## 工具调用

### feishu_ocr

```json
{
  "action": "image_url",
  "image_url": "https://example.com/image.jpg"
}
```

```json
{
  "action": "image_file",
  "file_path": "/path/to/image.jpg"
}
```

```json
{
  "action": "file_url",
  "file_url": "https://example.com/document.pdf"
}
```

```json
{
  "action": "file_path",
  "file_path": "/path/to/document.pdf"
}
```

### 返回结果

返回识别到的文字内容，格式为纯文本。

## 注意事项

- 飞书 OCR 完全免费，但有接口限流（QPS 限制）
- 识别效果较好，支持中文、英文、数字等
- 对于 PDF，建议先尝试飞书 OCR，如果效果不好再考虑百度 OCR（付费）
- 图片建议清晰、文字清晰可见
