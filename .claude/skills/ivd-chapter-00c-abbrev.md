---
name: ivd-chapter-00c-abbrev
description: "生成缩略语表。扫描所有已生成章节，收集专业缩略语。应在大部分章节完成后运行。"
type: chapter
chapter: "00c"
template: "templates/方案模板/00c_缩略语.md"
complexity: medium
requires:
  - "output/<name>/temp/ 下所有已生成的章节"
produces:
  - "output/<name>/temp/00c_缩略语.md"
---

# IVD Chapter 00c — 缩略语

## 数据源

扫描 `output/<name>/temp/` 下所有已生成的 `.md` 文件（00-06, 19 优先，07-18 如有则纳入）。

## 生成规则

1. 从所有章节正文中识别大写英文缩写（连续 2 个以上大写字母），如 IVD, PCR, LoB, LoD, LoQ, CI, SOP, NMPA, GCP, EQA, CLIA, CE, FDA, SD, CV, LoA, QC, RFID 等
2. 从 IFU 文件中提取产品特有的专业缩略语
3. 标准统计术语固定映射：
   - SD: 标准差 (Standard Deviation)
   - CV: 变异系数 (Coefficient of Variation)
   - LoA: 一致性界限 (Limits of Agreement)
   - CI: 置信区间 (Confidence Interval)
   - SOP: 标准操作规程 (Standard Operating Procedure)
   - LoB: 空白限 (Limit of Blank)
   - LoD: 检出限 (Limit of Detection)
   - LoQ: 定量限 (Limit of Quantitation)
4. 项目特有缩略语从考核试剂 IFU 中提取被测物缩写（如 cTnI, BNP, NT-proBNP 等）

## 验证

- 表中每行包含：缩略语 | 英文全称 | 中文全称
- 无 `【XXX_*】` 残留

## 产出

写入 `output/<name>/temp/00c_缩略语.md`。
