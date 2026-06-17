---
name: ivd-chapter-01-sponsor
description: "生成第一章：申办者信息。公司信息固定不变，直接透传模板。"
type: chapter
chapter: "01"
template: "templates/方案模板/01_申办者信息.md"
complexity: simple
requires: []
produces:
  - "output/<name>/temp/01_申办者信息.md"
---

# IVD Chapter 01 — 申办者信息

纯模板，深圳市新产业生物医学工程股份有限公司信息固定不变。直接读取模板内容作为输出。

## 固定信息（不可修改）
- 申办者：深圳市新产业生物医学工程股份有限公司
- 地址：深圳市坪山区坑梓街道...
- 联系人：王晟
- 联系电话：13699765239
- 统一社会信用代码：91440300708456292K

## 验证
```bash
grep -c '【' output/<name>/temp/01_*.md   # 必须为 0
```
