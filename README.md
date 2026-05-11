# Personal Knowledge Net

> 基于 Obsidian + TRAE SOLO 构建的个人学术知识库系统，面向深度学习时间序列预测研究。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [文件目录说明](#文件目录说明)
- [上手指南](#上手指南)
- [开发的架构](#开发的架构)
- [使用到的框架](#使用到的框架)
- [贡献者](#贡献者)
- [鸣谢](#鸣谢)

## 项目简介

本项目是一套面向学术研究的**个人知识库自动化系统**，以 Obsidian 为知识管理前端，实现了从 PDF 论文解析、知识节点提取、双向链接网络构建到**每周自动出题 + 邮件推送**的完整闭环。

核心理念来源于 Andrej Karpathy 的个人知识库搭建方法：**知识应该以原子化的方式组织，每个概念一个文件，通过双向链接形成网状图谱**。

**AI 不只是收集资料和总结方法，更重要的是形成独立的"我认为"——自主发现问题、提出判断、给出优化方案。**

## 功能特性

- 📄 **PDF 论文自动转换**：通过 Marker 将 PDF 论文转为 Markdown，保留公式、表格结构
- 🧠 **知识节点自动提取**：基于 DeepSeek LLM 从论文/笔记中提取概念，生成标准化 wiki 节点
- 🔗 **双向链接知识图谱**：Obsidian 原生支持，节点间通过 `[[双向链接]]` 形成网状关联
- ✅ **质量保障体系**：格式检查、死链检测、重复内容分析三重保障
- 📝 **每周自动出题**：分层出题（基础巩固 + 适度挑战 + 前沿思考），间隔重复巩固
- 📧 **邮件推送**：QQ 邮箱 SMTP 自动发送，支持云端提醒 + 本地轮询双系统
- ⭐ **题目收藏入库**：回答后的题目可收藏，沉淀为知识库的一部分

## 文件目录说明

```
personal-knowledge-net/
├── .github/workflows/          # GitHub Actions 云端提醒
│   └── weekly-reminder.yml     #   每周一自动发送"请打开SOLO"提醒邮件
│
├── .obsidian/                  # Obsidian 配置
│   ├── app.json                #   忽略目录、自动更新链接等配置
│   ├── core-plugins.json       #   启用的核心插件列表
│   └── snippets/               #   CSS 片段
│       └── quiz-graph-colors.css  # 收藏题目在图谱中显示为红色
│
├── _config/                    # ⚠️ 配置文件（含敏感信息，已脱敏）
│   ├── email_config.example.json  # 📌 邮件配置模板（需复制为 email_config.json 并填入真实信息）
│   ├── last_quiz_sent.json     #   本周出题发送状态（防重复）
│   └── quiz_history.json       #   历史出题记录
│
├── _templates/                 # Prompt 模板
│   └── weekly_quiz_prompt.md   #   每周出题规则模板（3:3:1 结构）
│
├── raw/                        # Marker 转换后的论文 Markdown（案例）
│   └── 2509.03505v2Limix/      #   LimiX 论文转换结果（示例）
│       ├── 2509.03505v2Limix.md    # 论文全文 Markdown
│       └── 2509.03505v2Limix_meta.json  # Marker 转换元数据
│
├── wiki/                       # 知识节点（案例：PatchTST 组）
│   ├── PatchTST模型.md         #   PatchTST 模型知识节点
│   ├── Patching（分块机制）.md  #   Patching 机制知识节点
│   ├── Channel-independence（通道独立）.md  #   通道独立策略知识节点
│   ├── 点级注意力问题.md        #   点级注意力问题知识节点
│   └── _quiz_archive/          #   收藏的题目与回答
│       └── PatchTST通道独立假设在乙烯裂解炉场景下成立吗.md  # 示例收藏
│
├── send_email.py               # 📌 邮件发送脚本（依赖 _config/email_config.json）
├── convert_pdfs.py             # PDF → Markdown 批量转换脚本（依赖 Marker）
├── process_manunote.py         # 笔记 → Wiki 节点处理脚本（依赖 DeepSeek API）
├── analyze_duplicates.py       # 重复内容检测脚本
├── analyze_format.py           # 格式合规检查脚本
├── analyze_links.py            # 双向链接死链检测脚本
├── OPTIMIZATION_PLAN.md        # 项目优化方案（Token 精简等）
├── .gitignore                  # Git 忽略规则
└── LICENSE                     # MIT 开源协议
```

### ⚠️ 敏感信息说明

本项目涉及以下需要用户自行配置的敏感信息：

| 文件 | 敏感内容 | 说明 |
|------|---------|------|
| `_config/email_config.json` | SMTP 授权码、邮箱地址 | **已加入 .gitignore，不会上传到仓库** |
| `.github/workflows/weekly-reminder.yml` | GitHub Secrets | 需在仓库 Settings → Secrets 中配置 `EMAIL_USERNAME` 和 `EMAIL_PASSWORD` |

**使用前请执行**：
```bash
cp _config/email_config.example.json _config/email_config.json
# 然后编辑 email_config.json，填入你的真实邮箱和授权码
```

### 📌 关键文件说明

- **`send_email.py`**：邮件发送核心脚本，读取 `_config/email_config.json` 中的配置。**如果未配置该文件，邮件功能不可用，但不影响其他功能。**
- **`convert_pdfs.py`**：调用 Marker（`marker_single`）将 PDF 转为 Markdown。需要安装 [Marker](https://github.com/VikParuchuri/marker) 并配置 `Dssk-wiki-Marker` conda 环境。
- **`process_manunote.py`**：调用 DeepSeek API 从笔记中提取知识节点。需要配置 DeepSeek API Key。
- **`_templates/weekly_quiz_prompt.md`**：定义了出题规则（3:3:1 比例、题目格式、用户背景等），SOLO 定时任务会读取此文件。

## 上手指南

### 开发前的配置要求

1. [Obsidian](https://obsidian.md/)（知识库前端）
2. [Python](https://www.python.org/) 3.10+
3. [Marker](https://github.com/VikParuchuri/marker)（PDF 转 Markdown，可选）
4. [DeepSeek API](https://platform.deepseek.com/)（知识提取，可选）
5. QQ 邮箱 SMTP 授权码（邮件推送，可选）

### 安装步骤

1. Clone the repo

```bash
git clone https://github.com/${GITHUB_USERNAME}/personal-knowledge-net.git
```

2. 在 Obsidian 中打开本项目文件夹作为 Vault

3. （可选）配置邮件推送

```bash
cp _config/email_config.example.json _config/email_config.json
# 编辑 _config/email_config.json，填入你的邮箱和 SMTP 授权码
```

4. （可选）配置 PDF 转换

```bash
conda activate Dssk-wiki-Marker  # 或你的 Marker 环境
python convert_pdfs.py            # 转换 _staging_pdf/ 中的 PDF
```

## 开发的架构

### 数据处理流水线

```
PDF 论文 ──→ _staging_pdf/ ──[convert_pdfs.py + Marker]──→ raw/ (MD + meta.json)
                                                              │
个人笔记 ──→ _ManuNote/ ──[process_manunote.py + DeepSeek]──→ wiki/ (知识节点)
                                                              │
                                                    ┌─────────┴──────────┐
                                                    │  质量保障脚本        │
                                                    │  analyze_format.py  │
                                                    │  analyze_links.py   │
                                                    │  analyze_duplicates │
                                                    └────────────────────┘
```

### 自动化出题系统

```
云端（GitHub Actions）          本地（SOLO Schedule）
┌──────────────────┐           ┌──────────────────────┐
│ 每周一 8:30      │           │ 每周一 8:30~12:30    │
│ 发提醒邮件       │  ──提醒──→│ 轮询出题并发邮件     │
│ "请打开SOLO"     │           │ 读知识库→生成问题     │
└──────────────────┘           │ →发送到QQ邮箱        │
                               └──────────────────────┘
```

### 出题结构（3:3:1 比例）

| 类型 | 频率 | 说明 |
|------|------|------|
| 🔰 基础巩固 × 3 | 每周 | 围绕已读 wiki 节点的基础概念理解 |
| 🚀 适度挑战 × 3 | 每两周 | 结合基础知识延伸到前沿方向 |
| 🔬 前沿思考 × 1 | 每月 | 对标顶会论文级别的开放性问题 |

### 知识节点模板

每个 wiki 节点遵循统一的模板格式：

```markdown
---
tags: [标签]
date: YYYY-MM-DD
source_refs: [来源论文/笔记ID]
---

一句话定义。

## 数学/逻辑推导
## 前提条件与适用边界
## [关联拓扑]
- [[相关概念]]：关系说明
```

## 使用到的框架

- [Obsidian](https://obsidian.md/) — 知识库前端（图谱、双向链接、标签）
- [Marker](https://github.com/VikParuchuri/marker) — PDF 转 Markdown 工具
- [DeepSeek API](https://platform.deepseek.com/) — 知识节点提取 LLM
- [TRAE SOLO](https://solo.trae.ai/) — AI 编程助手（项目构建、自动化、定时任务）
- [GitHub Actions](https://docs.github.com/en/actions) — 云端定时提醒

## 贡献者

欢迎提交 Issue 和 Pull Request。

## 鸣谢

- [Andrej Karpathy](https://x.com/karpathy) — 个人知识库搭建方法论
- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — 防止 LLM 幻觉的设计原则
- [Best_README_template](https://github.com/shaojintian/Best_README_template) — README 模板参考
- [dawidd6/action-send-mail](https://github.com/dawidd6/action-send-mail) — GitHub Actions 邮件发送
