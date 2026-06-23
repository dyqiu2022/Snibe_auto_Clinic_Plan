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

**表格格式要求：** 使用 Markdown pipe table 格式（`| 缩略语 | 英文 | 中文 |`），不要使用 HTML `<table>`。导出脚本 v5 已支持解析 pipe table。

示例格式：
```markdown
| 缩略语 | 英文全称 | 中文全称 |
| --- | --- | --- |
| IVD | In Vitro Diagnostic | 体外诊断 |
```
