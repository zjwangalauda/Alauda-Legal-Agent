# 🚀 Alauda Global Legal Agent - Release Notes

## [v6.1] - 2026-02-26 (Cloud-Native & Production Hardening Edition)

### 🔥 核心突破 (Major Features)
- **内置免费 AI 引擎 (Built-in Free AI Engine)**: 系统现已内置 Claude Haiku 推理引擎，用户无需配置任何 API Key 即可直接使用全部核心功能。零配置、开箱即用。
- **Streamlit Cloud 全球部署**: 系统已正式部署至 Streamlit Community Cloud，实现 7x24 小时全球在线访问，免运维高可用。
- **Redline 引擎全面重建 (DocxRedlineEngine Overhaul)**:
  - 文本匹配精度从 20 字符提升至 80 字符，大幅降低误标记率。
  - 引入 DOM 缓存机制，避免每次 `apply_redline()` 重复解析 XML，性能显著提升。
  - 新增视觉删除线标记 (Strikethrough Markup)，风险条款在 Word 文档中一目了然。

### 🔧 优化与修复 (Improvements & Fixes) — 共 9 项生产级缺陷修复
- **LangChain 依赖解耦**: 将 `has_langchain` (核心框架) 与 `has_google` (可选 Google 模型) 分离。修复了当 `langchain-google-genai` 未安装时，所有 LLM 路径（含 OpenAI/Claude）均回退至 Mock 模式的致命缺陷。
- **MultiDocReviewReport 安全访问**: Redline 引擎现使用 `hasattr()` 安全检查 `legal_reviews` / `hidden_backdoors` 字段，避免因数据结构差异导致的 `AttributeError` 崩溃。
- **Markdown 导出修复**: 修复了多文档报告导出时内容截断和格式错乱的问题，确保完整的三层视角报告可被完整导出。
- **Streamlit Secrets 注入修复**: 使用 `try/except` 包裹 `st.secrets.get()` 调用，解决无 `secrets.toml` 文件时抛出异常（而非返回空值）的问题。环境变量注入逻辑改为始终覆盖 (`if val:`)，确保 Cloud 环境 Secrets 正确传导至底层模块。
- **CLI 渲染器兼容**: 修复命令行模式下因 V5 数据结构变更导致的报告渲染崩溃。
- **`.doc` 格式声明移除**: 移除了对旧版 `.doc` 格式的虚假支持声明（仅支持 `.docx`/`.pdf`/`.txt`）。
- **依赖清单完善**: `requirements.txt` 补全了 `langchain-core`, `langchain-openai`, `langchain-anthropic`, `lxml` 等遗漏依赖。
- **安全加固**: `.gitignore` 强化，确保 `.env`, `.streamlit/secrets.toml`, `.venv/`, `.DS_Store` 等敏感文件永不进入版本控制。
- **冗余文件清理**: 移除了 `.html`, `.pdf`, `.png` 等构建产物，保持仓库整洁。

---

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
