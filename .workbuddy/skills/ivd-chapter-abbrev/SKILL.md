---
title: "缩略语"
summary: "生成缩略语章节，收集所有章节中出现的专业缩略语"
read_when:
  - Phase 5 缩略语生成
---

# IVD Chapter 00c — 缩略语

## 数据源

| ID | 来源 | 提取字段 |
|----|------|---------|
| DS-01 | Phase 1-4 所有已生成章节 | 文中出现的所有专业缩略语 |

## 工具调用

1. 扫描 Phase 1-4 所有已生成章节，收集文中出现的专业缩略语
2. 不得遗漏任一章节
3. 按字母顺序排序

## 产出

写入 `output/<name>/temp/00c_缩略语.md`。

**表格格式要求：** 必须使用 HTML `<table>` 格式，不得使用 Markdown pipe table（`| ... |`）。导出脚本仅解析 HTML 表格，pipe table 不会被渲染为 Word 表格。

示例格式：
```html
<table><tr><td><p>缩略语</p></td><td><p>英文全称</p></td><td><p>中文全称</p></td></tr><tr><td><p>IVD</p></td><td><p>In Vitro Diagnostic</p></td><td><p>体外诊断</p></td></tr></table>
```
