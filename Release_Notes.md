# 🚀 Alauda Global Legal Agent - Release Notes

## [v5.0] - 2026-02-22 (Multi-Role Copilot & Web Dashboard Edition)

### 🔥 核心突破 (Major Features)
- **多角色决策中枢 (Multi-Role Copilot)**: 彻底重构了底层数据契约，Agent 不再局限于法务找错，而是化身“三重商业幕僚”：
  - **👨‍💼 核心管理层 (CXO) 审批台**: 自动生成带有红绿灯状态的最终签约决议、致命阻碍(Deal Breakers)提取及战略博弈指导。
  - **📈 运营与商务履约看板**: 专为 PMO 与财务打造。自动从海量合同文本中提取关键的账期节奏、维保年限、违约罚金，并评估其对现金流的实际影响。
  - **⚖️ 法务合规防御阵地**: 保留强大的红黑线对照与多文档后门嗅探能力。
- **现代化可视化看板 (Web UI Dashboard)**: 引入了基于 Streamlit 的 Web App 工作台，深度融合 Alauda 官网企业级视觉规范 (Navy/Blue/Slate 沉浸色系)，实现零代码极简交互上传。
- **模型无关化架构 (Agnostic LLM Engine)**: 底层解耦 Google Gemini，现在系统在 Web 端支持下拉动态切换 OpenAI (gpt-4o), Anthropic (Claude 3.5), 或接入公司私有化兼容网关。

### 🔧 优化与修复 (Improvements & Fixes)
- **中英双语自适应输出 (Dynamic Language Sensing)**: 极大改善国内合同审核体验。若输入合同为中文，系统将强行压制英文 Legal English 偏好，全量输出符合中国法律行规的中文修改建议。
- **UI 组件重绘**: 修复了 Web App 在浅色模式下的字体反白不可见问题；强制染色侧边栏控制图标，确保无死角的视觉清晰度。
- **CLI 渲染器对齐**: 修复了通过命令行运行多文档审计时由于 V5 数据结构改变导致的渲染崩溃。

---

## [v4.0] - 2026-02-21 (Semantic LLM & Multi-Doc Knowledge Graph Edition)

### 🔥 核心突破 (Major Features)
- **底层架构重写**: 将基于正则表达式的 V1/V2 “老旧专家系统”彻底进化为基于 **Gemini 1.5/3.1 Pro 百万上下文**的大模型语义推理架构。
- **多文档图谱交叉审查 (Multi-Doc Graph Auditing)**: 首创针对大型 B2B 采购案卷的联查模式。通过提取文件的 `Order of Precedence` (效力优先级)，构建层级树，并能在极度隐蔽的附件 (如 SOW) 中精准嗅探试图推翻主协议红线的商业后门陷阱。
- **结构化防御 (Pydantic Output)**: 利用 LangChain 的强类型输出控制，将 LLM 不羁的语言强制收束至统一的业务评估结构中。

---

## [v1.0 - v3.0] - 早期版本 (Regex Expert System)
- 基于 Python 正则表达式与关键词扫描。
- 确立了灵雀云 (Alauda) SaaS 商业底线的 6 大维度规则库（双轨制赔偿、默示验收、限制支持范围等）。
