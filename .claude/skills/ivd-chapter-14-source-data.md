---
name: ivd-chapter-14-source-data
description: "生成第十四章：同意直接访问源数据文件。纯模板，直接透传。"
type: chapter
chapter: "14"
template: "templates/方案模板/14_关于同意直接访问源数据文件的说明.md"
complexity: simple
requires: []
produces: ["output/<name>/temp/14_关于同意直接访问源数据文件的说明.md"]
---
# IVD Chapter 14 — 同意直接访问源数据文件
纯模板无占位符。直接透传。
验证: `grep -c '【' output/<name>/temp/14_*.md` 必须为 0
