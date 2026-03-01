# 🚀 Alauda Global Legal Agent (V6.1) 用户手册

**版本**: 6.2.1 (Security & Quality Hardening Edition)
**更新日期**: 2026年3月2日
**适用对象**: Alauda (灵雀云) 法务、交付、商务与高管团队

---

## 云端访问

- **Streamlit Cloud 官方地址**: [Alauda Global Legal Agent](https://alauda-legal-agent.streamlit.app/)
*(建议收藏此链接，支持电脑与移动端访问，无需安装任何软件)*

---

## 目录

1. [核心愿景与架构演进](#1-核心愿景与架构演进)
2. [V5 独家特性：三重视角 Copilot](#2-v5-独家特性三重视角-copilot)
3. [多文档关联审计机制](#3-多文档关联审计机制)
4. [SaaS 商业红线与法务底线](#4-saas-商业红线与法务底线)
5. [操作指南 (Web App, CLI, Docker & Testing)](#5-操作指南-web-app-与-cli)
6. [输出报告实战示例](#6-输出报告实战示例)

---

## 1. 核心愿景与架构演进

本手册旨在为 **Alauda (灵雀云)** 提供一套基于端到端大语言模型 (LLM) 的自动化合同审查系统。我们的愿景是将资深法务 Partner 的商业嗅觉与 AI 的全景阅读能力结合，从而在极短时间内封堵 B2B 合同中的致命隐患。

经过架构迭代，系统目前已演进至 **V6.2.1 (Security & Quality Hardening Edition)**：
- **内置免费 AI 引擎**：系统已内置 Claude Haiku 推理引擎。用户无需配置 API Key 即可使用全部核心功能，开箱即用。高级用户仍可在侧边栏切换至 OpenAI/Anthropic/Google 等自有模型。
- **模型无关化 (Agnostic LLM)**：底层脱离单一模型绑定，动态支持 Google Gemini, OpenAI, Claude 以及公司内网私有化模型网关。
- **结构化防御 (Pydantic)**：通过强类型 JSON 数据契约，强制大模型根据原文语言（中/英）自适应输出地道的法律修改建议。
- **现代化 Web UI**：采用 Streamlit 构建了带有 Alauda 企业视觉体系的高级可视化数据看板，彻底告别枯燥的命令行。
- **Redline 引擎重建**：全新的 Word 文档 Track Changes 引擎，支持 80 字符精准匹配、DOM 缓存与视觉删除线标记。
- **CI/CD 与容器化 (V6.2)**：新增 GitHub Actions 自动化流水线（ruff lint + pytest）、Docker 容器化部署与 12 个核心单元测试。

---

## 2. V5 独家特性：三重视角 Copilot

V5 版本最大的突破在于：系统不再是一个单纯的“找错机器”，而是化身为拥有“三重人格”的高级商业幕僚。针对每一份上传的合同或案卷，系统会拆解为三层金字塔视角：

1. 👨‍💼 **核心管理层 (CXO) 审批台 (塔尖)**：
   - 给出极其明确的决策建议（【建议直接签约】/【有条件通过】/【强烈建议拒签】）。
   - 提炼阻碍签约的“致命因素 (Deal Breakers)”。
   - 撰写包含利益交换和让步红线的“战略博弈指导”。
2. 📈 **运营与商务履约看板 (中层)**：
   - 为 PMO 和财务团队自动提取庞杂文本中的账期、首付比例、服务期、罚金条款。
   - 自动测算并提示对公司现金流与交付成本的真实业务影响。
3. ⚖️ **法务合规与红线防御阵地 (基座)**：
   - 逐条列出违反公司 SaaS 政策的高危/中危条款。
   - 给出法务溯源分析，以及可直接用于红线谈判的修正建议 (Redline)。

---

## 3. 多文档关联审计机制

大型 B2B 客户经常采用**“明修栈道，暗度陈仓”**的策略：在严格的《主协议 GFA》中答应所有底线，却在某个交付团队草签的《服务说明书 SOW》附件中写上“本 SOW 拥有最高优先级，且供应商需承担无限数据连带责任”。

**Agent 的跨文档图谱工作流：**
1. **构建效力拓扑**：自动抓取所有文件中的 `Order of Precedence`，梳理出一张“谁管谁”的效力层级树。
2. **后门嗅探 (Backdoor Detection)**：利用百万级 Token 上下文，将高优先级的附件与低优先级主合同的红线进行交叉对比。一旦发现低级别文件中的保护被高级别文件越权推翻，即触发红色防线警报并提供定向爆破条款。

---

## 4. SaaS 商业红线与法务底线

Agent 严格捍卫以下 6 条 SaaS 商业生命线：

| 监控维度 | 风险红线判定标准与业务逻辑 |
|------|-----------------|
| **订阅计量** | 🔴 拒绝买断/无限使用权 → 🟢 必须基于 Node/Core 等具体 Unit 计量。<br>*防范客户购买一套授权后在企业内无限制复制。* |
| **赔偿责任** | 🔴 拒绝无限赔偿或包含数据丢失 → 🟢 上限为 12个月订阅费 (EULA限$50)。<br>*实施严格的“双轨制”风控，明确排除间接损失。* |
| **知识产权** | 🔴 拒绝派生品归属客户 (Work for Hire) → 🟢 坚守核心 PaaS 底座所有权。<br>*防止被单一客户买断导致核心代码闭源。* |
| **验收结项** | 🔴 拒绝单边书面确认或无限循环拒收 → 🟢 必须包含 10 个工作日默示验收。<br>*杜绝客户利用内部流程拖延 FAC 结项，强保尾款结算。* |
| **SLA响应** | 🔴 拒绝 <30 分钟内 / 24x7 无限支持 → 🟢 匹配 P1 30mins, P2 2hrs 上限。<br>*拒绝脱离一线运维中心 (ROTC) 实际承受能力的承诺。* |
| **支持范围** | 🔴 拒绝驻场或第三方软件兜底 → 🟢 仅限 Alauda 认证环境内的远程支持。<br>*明确排除定制代码开发和非认证组件排障以控制成本。* |

---

## 5. 操作指南 (Web App 与 CLI)

### 5.1 云端直接使用 (推荐)
访问 [Alauda Global Legal Agent](https://alauda-legal-agent.streamlit.app/) 即可立即使用，无需安装任何软件。

系统已内置免费 AI 引擎 (Claude Haiku)，**无需配置 API Key**。
- **单文档模式**：直接上传 PDF/Word (.docx)。
- **多文档模式**：将整个案卷打包为 `.zip` 上传，体验震撼的效力拓扑与后门雷达。
- **自带模型 (可选)**：高级用户可在左侧边栏下拉切换至 OpenAI/Anthropic/Google 等自有模型并填入 API Key。

### 5.2 本地部署 (开发者)
```bash
# 激活环境
source .venv/bin/activate
# 启动企业级 Web 看板
streamlit run web_app.py
```
启动后访问 `http://localhost:8501`。

### 5.3 CLI 极客模式
对于技术人员批量处理任务，也可使用原生命令行：
```bash
# 审查单个文件
python3 alauda_legal_agent.py -f contract.txt -o report.md

# 审查多文档目录
python3 alauda_legal_agent.py -d ./customer_bundle/ -o report.md
```

### 5.4 Docker 容器化部署
```bash
docker build -t legal-agent .
docker run -p 8501:8501 legal-agent
```
启动后访问 `http://localhost:8501`。

### 5.5 测试与代码质量
```bash
pip install pytest ruff
# 运行单元测试（38 个用例）
python -m pytest tests/ -v
# 代码质量检查
ruff check .
```

---

## 6. 输出报告实战示例

*(以下为针对某金融机构真实案卷 V5 版多角色输出节选)*

### 👨‍💼 核心管理层 (CXO) 审批台
- **最终决议**：🔴 **【有条件通过(必须强拆后门)】**
- **致命阻碍 (Deal Breakers)**：SOW附件利用优先权推翻了GFA的赔偿上限，带来针对银行数据的无限索赔敞口；且未包含默示验收。
- **战略博弈指导 (Strategic Playbook)**：这是战略级标杆客户，且首付高达40%能极大缓解现金流。建议不要直接拒签，应由法务 VP 出面，在最高优先级的 Order Form 中强制打上免责补丁。同时在交付端加派资深架构师对冲验收延期风险。

### 📈 运营与商务履约看板
| 核心要素 | 合同摘要 | 运营影响测算 |
| :--- | :--- | :--- |
| **合同总金额** | 300万人民币 | 大单，高营收，具有战略意义 |
| **付款节奏** | 20% - 40% - 40% (分三年付) | 首付偏低，存在长达两年的垫资交付期资金压力 |
| **维保周期** | 自签收后长达36个月 | 维保人力成本极高，需单独核算维保利润率 |

### ⚖️ 法务合规与红线防御阵地 (Legal Risk Matrix)

**💥 发现后门 #1：知识产权 (IP Rights) - 平台衍生品强制归属客户 🔴 HIGH**
- **🏰 主协议防线 (Master Clause)**:
  > GFA 11.1(3): MegaBank owns all rights, title and interest in and to Intellectual Property Rights developed during the course of providing Services... including enhancements, modifications or derivative works of materials...

- **🗡️ 越权覆盖点 (Overriding Clause in `General Terms.docx`)**:
  > Software Module 5.2 再次强化: Ownership of the Intellectual Property Rights in any customisations... will be governed by the relevant Service Module.

**💡 致命风险溯源分析 (Risk Trace Analysis)**:
客户在主框架中规定，无论原先是谁的知识产权（包括 Alauda 核心底座），只要在服务过程中产生了 enhancements(增强) 或 derivative works(衍生品)，所有权全部归属客户。这意味着 Alauda 实施团队在驻场时写的外围插件、架构优化脚本都会在法律上被收归银行所有，严重阻碍 Alauda 将这些实践标准化进下一次产品迭代的权利。

**✅ 法务强拆建议 (Suggested Counter-Measure)**:
```text
删除 GFA 11.1(3) 中的 'enhancements, modifications or derivative works...' 并在 Order Form 中利用最高优先级添加特约保护：
'Notwithstanding General Terms 11.1, Supplier retains all ownership to its pre-existing core platform and any derivative works thereof. MegaBank only owns custom deliverables explicitly stated as Work for Hire.'
```

---
*Alauda Global Legal Agent - 您的智能法务与商务中枢引擎。*
