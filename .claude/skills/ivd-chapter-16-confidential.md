---
name: ivd-chapter-16-confidential
description: "生成第十六章：保密原则。纯模板，直接透传。"
type: chapter
chapter: "16"
template: "templates/方案模板/16_保密原则.md"
complexity: simple
requires: []
produces: ["output/<name>/temp/16_保密原则.md"]
---
# IVD Chapter 16 — 保密原则
纯模板无占位符。直接透传。
验证: `grep -c '【' output/<name>/temp/16_*.md` 必须为 0
