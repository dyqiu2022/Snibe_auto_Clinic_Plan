---
name: ivd-chapter-17-roles
description: "生成第十七章：各方承担的职责。纯模板，直接透传。"
type: chapter
chapter: "17"
template: "templates/方案模板/17_各方承担的职责.md"
complexity: simple
requires: []
produces: ["output/<name>/temp/17_各方承担的职责.md"]
---
# IVD Chapter 17 — 各方承担的职责
纯模板无占位符。直接透传。
验证: `grep -c '【' output/<name>/temp/17_*.md` 必须为 0
