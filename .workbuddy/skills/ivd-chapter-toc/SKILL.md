---
title: "目录"
summary: "生成带 Markdown 锚点的目录，包含全部章节标题"
read_when:
  - Phase 6 目录生成
---

# IVD Chapter 00d — 目录

## 数据源

| ID | 来源 | 提取字段 |
|----|------|---------|
| DS-01 | Phase 1-4 所有已生成章节 | 所有标题（#、##、###） |

## 工具调用

1. 读取所有已完成章节的标题（#、##、###）
2. 自动生成带 markdown 锚点的目录

## 产出

写入 `output/<name>/temp/00d_目录.md`
