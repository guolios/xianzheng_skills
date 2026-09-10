# PPT制作 Skills 合集

本文件夹汇集了6款优质的AI PPT制作技能，覆盖从原生PowerPoint生成、网页PPT设计、幻灯片图像生成到动态演示等多种场景。

## 技能列表

### 1. PPT Master
**仓库**: [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)

**简介**: AI驱动的原生PowerPoint生成工具，可以从任意文档自动生成PPT。

**特点**:
- 从文档/Markdown一键生成原生 .pptx 文件
- 支持多种模板和主题
- 智能排版与内容组织
- 跨平台兼容

**适用场景**: 需要生成可编辑的PowerPoint文件、学术汇报、商务演示

---

### 2. Guizang PPT Skill · 归藏PPT
**仓库**: [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)

**简介**: 适配Agent环境的网页PPT技能，生成单文件HTML横向翻页PPT，内置排练与演讲者模式。

**特点**:
- 两套视觉系统：Style A（电子杂志×电子墨水）、Style B（瑞士国际主义）
- 单文件HTML输出，无需依赖
- 内置演讲者模式和排练计时
- PPT配图与多平台封面生成
- 支持 Claude Code / Codex 等Agent环境

**适用场景**: 技术分享、产品发布、个人演讲、叙事型演示

---

### 3. Huashu Design · 花叔设计
**仓库**: [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)

**简介**: 一句话生成可交付的设计——产品发布动画、App原型、PPT、信息图。

**特点**:
- 一句话prompt生成专业级设计
- 60 种内置 HTML 原生风格库（网页/PPT/信息图各 20 种）
- 支持品牌资产导入（Logo、色板、UI截图）
- 输出可编辑的PPT、动画、信息图
- 跨Agent通用（Claude Code、Cursor、Codex等）

**适用场景**: 产品发布动画、APP原型设计、品牌演示、信息图制作

---

### 4. PPTAgent
**仓库**: [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent)

**简介**: 中科院开发的PPT智能体，支持多智能体协作生成专业演示文稿。

**特点**:
- 多智能体协作架构（Planner/Design/Research等）
- 支持从PDF/文档自动提取内容
- 内置多种高校模板（清华、中科院等）
- 支持HTML转PPTX
- 多语言支持

**适用场景**: 学术报告、科研汇报、高校教学、专业演示

---

### 5. Anthropic PPTX
**仓库**: [anthropics/skills](https://github.com/anthropics/skills)

**简介**: Anthropic 官方出品的 .pptx 创建、编辑与分析技能，可精确控制原生 PowerPoint 文件的排版、图表、模板与演讲者备注。

**特点**:
- 通过 `pptxgenjs` 脚本创建可编辑的原生 .pptx
- 支持解压→编辑 XML→重打包流程增删改幻灯片
- 内置缩略图预览、幻灯片复制、清理与文件校验脚本
- 丰富的配色方案、版式与排版设计规范
- 包含视觉 QA、内容 QA 与文件 QA 全流程自检

**适用场景**: 需要生成可编辑、高精度原生 .pptx 文件、套用模板或进行文件级校验的场景

---

### 6. Baoyu Slide Deck · 宝玉Slide
**仓库**: [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)

**简介**: 将内容生成为专业幻灯片图像（仅用于阅读与分享）的 AI 技能，先生成大纲与风格指令，再逐张生成幻灯片图片。

**特点**:
- 17 种风格预设（蓝图、黑板、极简、水彩、复古等），多维可自定义
- 支持自定义听众、语言、页数、参考图与批处理生成
- 生成后自动合并为 PPTX / PDF
- 内置确认流程与大纲/提示词复查机制
- 跨 Agent 通用（Codex、Cursor 等）

**适用场景**: 面向社交媒体分享、内容阅读与传播的图文型幻灯片

---

## 快速选择指南

| 需求 | 推荐技能 | 输出格式 |
|------|----------|----------|
| 需要原生 .pptx 文件 | PPT Master / PPTAgent / Anthropic PPTX | .pptx |
| 套用现成模板、精确控制版式 | Anthropic PPTX | .pptx |
| 图文型幻灯片、社交媒体分享 | 宝玉Slide | 图片 / .pptx / PDF |
| 网页展示、在线分享 | 归藏PPT / 花叔设计 | HTML |
| 动画效果、产品发布 | 花叔设计 | HTML / 视频 |
| 学术/科研汇报 | PPTAgent | .pptx |
| 个人风格、叙事演讲 | 归藏PPT | HTML |
| 快速原型、信息图 | 花叔设计 | HTML / 图片 |

## 使用说明

每个技能文件夹内都有详细的 `README.md` 和 `SKILL.md` 文件，请参考各技能的文档进行安装和使用。

### 通用安装方式

大多数技能支持通过 skills 管理器安装：

```bash
# 例如安装 huashu-design
npx skills add alchaincyf/huashu-design
```

具体安装方式请参考各技能的官方文档。

## 许可证

各技能遵循其各自的开源许可证，请参考各项目内的 LICENSE 文件。
