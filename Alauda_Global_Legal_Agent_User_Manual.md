# 🚀 Alauda Global Legal Agent 用户手册

**版本**: 2.0  
**更新日期**: 2026年2月20日  
**适用对象**: Alauda (灵雀云) 法务团队

---

## 目录

1. [核心愿景](#1-核心愿景)
2. [Agent 角色配置](#2-agent-角色配置)
3. [审核维度详解](#3-审核维度详解)
   - 3.1 销售合同审核维度
   - 3.2 技术支持合同审核维度
4. [标准红线知识库](#4-标准红线知识库)
5. [操作指南](#5-操作指南)
6. [输出报告说明](#6-输出报告说明)
7. [常见问题 FAQ](#7-常见问题-faq)
8. [附录](#8-附录)

---

## 1. 核心愿景

本手册旨在为 **Alauda (灵雀云)** 的法务团队提供一套基于 AI 的自动化合同审核方案。通过在 OpenCode 中集成 Red Hat 的法律逻辑与严格的商业风险过滤，将原本数小时的初审缩短至 **5 分钟**。

### 核心价值

| 维度 | 传统方式 | AI Agent 方式 |
|------|---------|---------------|
| 初审时间 | 2-4 小时 | 5 分钟 |
| 风险覆盖 | 依赖个人经验 | 13 个维度全覆盖 |
| 修订建议 | 手动撰写 | 自动生成 Legal English |
| 一致性 | 因人而异 | 统一标准 |

---

## 2. Agent 角色配置

在 OpenCode 的 Agent Settings 中新建角色，填入以下指令：

### 角色名称
**Alauda 全球法律与运营架构师**

### 底层逻辑 (Persona)

```
你是一名精通全球通用法律的开源软件领域专家，专注于为 Alauda (灵雀云) 
提供合同风险审核服务。

核心原则：
1. 赔偿限额：坚守 12 个月订阅费原则，拒绝任何超过 12 个月已付金额的赔偿要求
2. 知识产权 (IP)：区分"定制成果"与"平台核心"。Alauda 必须保留核心 PaaS 平台及其衍生作品的所有权
3. 验收条款：将"主观验收"转为带有 10 天缓冲期的"默示验收"
4. 救济排他性：确保 Fee Reductions 是延期或服务不达标的唯一救济措施

合同类型识别：
- 销售合同：关注赔偿、IP、验收、终止等商业条款
- 技术支持合同：关注 SLA、支持范围、培训承诺、支持期限等运维条款
```

---

## 3. 审核维度详解

### 3.1 销售合同审核维度 (7 个)

| 维度 | 英文名 | 风险等级判定标准 |
|------|--------|-----------------|
| **订阅计量** | Subscription Metrics | 🔴 无限制使用 / 企业级授权 → 🟢 基于核心/节点计量 |
| **赔偿条款** | Liability | 🔴 3倍赔偿 / 无上限 → 🟢 12个月订阅费 (免费版 $50) |
| **知识产权** | IP | 🔴 客户拥有所有衍生作品 → 🟢 Alauda 保留核心平台权 |
| **验收条款** | Acceptance | 🔴 需书面批准 / 客户满意为准 → 🟢 10天默示验收 |
| **终止条款** | Termination | 🔴 可立即终止 / 无终止权 → 🟢 30-90天通知期 |
| **适用法律** | Governing Law | 🔴 客户专属管辖 → 🟢 中立法域 |
| **数据保护** | Data Protection | 🔴 供应商独自承担数据责任 → 🟢 双方共同合规 |

### 3.2 技术支持合同审核维度 (7 个)

| 维度 | 英文名 | 风险等级判定标准 |
|------|--------|-----------------|
| **SLA 响应时间** | SLA Response | 🔴 Level 1 响应 < 30分钟 → 🟢 Level 1: 30分钟 |
| **支持范围** | Support Scope | 🔴 无限制支持 / 驻场 / 包含定制代码 → 🟢 明确排除项及前置认证 |
| **责任排除** | Exclusion of Liability | 🔴 对所有损失负责 → 🟢 排除间接损失 |
| **培训承诺** | Training Commitment | 🔴 >100小时/年 🟡 60-80小时/年 → 🟢 ≤40小时/年 |
| **支持期限** | Support Duration | 🔴 终身支持 🟡 整个合同期 → 🟢 18个月 |
| **访问权限** | Access Rights | 🔴 直接访问生产环境 → 🟢 仅屏幕共享 |
| **支持终止** | Support Termination | 🔴 无终止权 🟡 客户可拒绝 → 🟢 90天通知终止 |

---

## 4. 标准红线知识库

### 4.1 销售合同红线矩阵

#### 订阅计量 (Subscription Metrics)

| 监控维度 | 风险点示例 | Alauda 标准回改方案 | 理由 |
|:--------|:-----------|:-------------------|:-----|
| 授权范围 | 企业级无限制使用权 (Enterprise-wide/Unlimited) | 基于明确的单位(Unit)计量授权 | 对标RedHat/SUSE商业模式，确保商业收益匹配 |

#### 赔偿条款 (Liability)

| 监控维度 | 风险点示例 | Alauda 标准回改方案 | 理由 |
|:--------|:-----------|:-------------------|:-----|
| 赔偿责任 | 赔偿限额为已付金额的 3 倍 / 免费版无上限 | 商业版限额过去12个月已付费，EULA免费软件限额$50 | 实施双轨制风险隔离对冲 |

#### 知识产权 (IP)

| 监控维度 | 风险点示例 | Alauda 标准回改方案 | 理由 |
|:--------|:-----------|:-------------------|:-----|
| IP 归属 | 衍生作品及增强功能所有权归甲方 | 定制部分归甲方，但核心架构优化权归 Alauda | 保护核心产品分发权，避免被单一银行绑定 |

#### 验收条款 (Acceptance)

| 监控维度 | 风险点示例 | Alauda 标准回改方案 | 理由 |
|:--------|:-----------|:-------------------|:-----|
| 验收付款 | 必须由甲方书面确认才可开票付款 | 交付 10 个工作日内未书面拒绝则视为验收合格 | 解决现金流被流程拖延的问题 |

#### 违约救济 (Remedies)

| 监控维度 | 风险点示例 | Alauda 标准回改方案 | 理由 |
|:--------|:-----------|:-------------------|:-----|
| 违约赔偿 | 费用核减不排除进一步索赔 | 明确 Fee Reductions 是延期等违约的唯一救济手段 | 确保违约成本的确定性 |

### 4.2 技术支持合同红线矩阵

#### SLA 响应时间 (SLA Response)

| 监控维度 | 风险点 | Alauda 标准 | 理由 |
|:--------|:-------|:------------|:-----|
| Level 1 响应 | < 30 分钟内响应 | 30 分钟初始响应 | 匹配公司最新运营标准 |
| Level 2 响应 | < 2 小时内响应 | 2 小时初始响应 | 同上 |
| Level 3/4 响应 | < 4 小时 / 8 小时 | 4 小时 / 8 小时初始响应 | 同上 |
| 支持模式 | 24/7 全天候 | 可协商时段 | 考虑运营成本 |

#### 支持范围 (Support Scope)

| 监控维度 | 风险点 | Alauda 标准 | 理由 |
|:--------|:-------|:------------|:-----|
| 定制与驻场 | 包含定制开发(Custom code)或驻场支持(On-site) | 明确排除定制开发与现场服务 | 对标Alauda原厂标准服务条款，避免范围失控 |
| 第三方组件 | 包含所有第三方软件的支持 | 仅支持Alauda显式认证环境 | 减轻运维兜底压力 |

#### 培训承诺 (Training Commitment)

| 监控维度 | 风险点 | Alauda 标准 | 理由 |
|:--------|:-------|:------------|:-----|
| 年度培训时长 | 72 小时/年 | 40 小时/年 | 避免培训成本失控 |
| 培训范围 | 任何软件相关主题 | 限定主题列表 | 控制范围蔓延 |

#### 支持期限 (Support Duration)

| 监控维度 | 风险点 | Alauda 标准 | 理由 |
|:--------|:-------|:------------|:-----|
| 支持期限 | 整个合同期间 | 18 个月 (当前版本 + 前一版本) | 控制长期维护成本 |
| 版本支持 | 所有历史版本 | 仅限当前及前一主要版本 | 避免"僵尸版本"维护负担 |

#### 支持终止 (Support Termination)

| 监控维度 | 风险点 | Alauda 标准 | 理由 |
|:--------|:-------|:------------|:-----|
| 终止权 | 客户可拒绝终止 | 双方均可 90 天通知终止 | 保持业务灵活性 |

---

## 5. 操作指南

### 5.1 安装与配置

```bash
# 1. 脚本位置
/Users/rootwang/opencode/Legal/alauda_legal_agent.py

# 2. 运行权限 (首次使用)
chmod +x /Users/rootwang/opencode/Legal/alauda_legal_agent.py
```

### 5.2 基本使用

#### 方式一：直接输入合同文本

```bash
python3 /Users/rootwang/opencode/Legal/alauda_legal_agent.py -t "合同文本内容..."
```

#### 方式二：从文件读取合同

```bash
# 支持 .txt, .md, .json 格式
python3 /Users/rootwang/opencode/Legal/alauda_legal_agent.py -f contract.txt
```

#### 方式三：保存报告到文件

```bash
python3 /Users/rootwang/opencode/Legal/alauda_legal_agent.py -f contract.txt --output report.md
```

### 5.3 输出格式选项

| 参数 | 说明 |
|------|------|
| `-o markdown` | 输出 Markdown 格式 (默认) |
| `-o json` | 输出 JSON 格式 (便于程序调用) |
| `--no-mode-b` | 仅输出 Mode A 对比表，不包含修订建议 |

### 5.4 完整命令示例

```bash
# 生成完整报告 (Mode A + Mode B)
python3 alauda_legal_agent.py -f contract.txt --output review_report.md

# 仅生成风险对比表
python3 alauda_legal_agent.py -f contract.txt --no-mode-b --output risk_table.md

# 生成 JSON 格式 (用于系统集成)
python3 alauda_legal_agent.py -f contract.txt -o json --output report.json
```

---

## 6. 输出报告说明

### 6.1 Mode A: 风险对比表

Mode A 提供结构化的风险概览，便于快速识别问题条款：

```
| 监控维度 | 原文摘要 | 风险等级 | Alauda 标准要求 | 风险原因 |
| :--- | :--- | :---: | :--- | :--- |
| 赔偿条款 | ... | 🔴 HIGH | 12个月订阅费 | 赔偿倍数过高 (3倍) |
```

**风险等级图标说明**：
- 🔴 **HIGH** - 需要立即修改，不可接受
- 🟡 **MEDIUM** - 建议修改，可协商
- 🟢 **LOW** - 符合 Alauda 标准
- ⚪ **N/A** - 未检测到相关条款

### 6.2 Mode B: 建议修订文本

Mode B 提供可直接使用的 Legal English 修订建议：

```
### 赔偿条款 (Liability)

**❌ 原条款风险**: 赔偿倍数过高 (3倍)

**✅ 建议修订**:
```
Supplier's total aggregate liability shall not exceed the total fees 
paid by Customer in the 12 months preceding the claim.
```
```

### 6.3 审核摘要

报告末尾提供统计数据：

```
| 风险等级 | 数量 |
| :---: | :---: |
| 🔴 高风险 | 1 |
| 🟡 中风险 | 3 |
| 🟢 低风险 | 9 |
```

---

## 7. 常见问题 FAQ

### Q1: 如果不适用新加平台法律怎么办？

Agent 会自动检测 **Governing Law** 章节并提醒法务注意司法管辖区差异。不同法域可能需要调整审核标准。

### Q2: Agent 漏掉了某个条款怎么办？

点击 **"Add to Knowledge"**，下次审核同类合同时（如 UOB 或 OCBC）它会自动识别。同时可以将新规则添加到脚本中的 `benchmark` 配置。

### Q3: 如何处理俄语/英语混合合同？

脚本已支持多语言合同识别，会自动处理俄语 (如 "поддержк", "обучен") 和英语混合文本。

### Q4: 风险等级是否可以调整？

可以。在脚本的 `risk_rules` 配置中修改正则规则，将某些规则从 `high` 移到 `medium` 或反之。

### Q5: 如何添加新的审核维度？

在脚本的 `benchmark` 字典中添加新类别：

```python
"new_category": {
    "keywords": [r"keyword1", r"keyword2"],
    "redline": "Alauda 标准要求",
    "standard_clause": "标准条款文本",
    "rationale": "理由说明",
    "risk_rules": {
        "high": [(r"pattern", "风险原因")],
        "medium": [(r"pattern", "风险原因")]
    }
}
```

### Q6: 如何处理 Word/PDF 格式的合同？

**方法一**：使用 macOS 自带工具转换
```bash
textutil -convert txt contract.docx -output contract.txt
```

**方法二**：直接复制粘贴合同文本到命令行
```bash
python3 alauda_legal_agent.py -t "$(pbpaste)"
```

---

## 8. 附录

### 8.1 审核维度完整列表

| 序号 | 维度代码 | 中文名 | 适用合同类型 |
|:----:|:---------|:-------|:-------------|
| 1 | liability | 赔偿条款 | 销售合同 |
| 2 | ipr | 知识产权 | 销售合同 |
| 3 | acceptance | 验收条款 | 销售合同 |
| 4 | termination | 终止条款 | 销售合同 |
| 5 | governing_law | 适用法律 | 销售合同 |
| 6 | data_protection | 数据保护 | 销售合同 |
| 7 | sla_response | SLA 响应时间 | 技术支持合同 |
| 8 | support_scope | 支持范围 | 技术支持合同 |
| 9 | exclusion_liability | 责任排除 | 技术支持合同 |
| 10 | training_commitment | 培训承诺 | 技术支持合同 |
| 11 | support_duration | 支持期限 | 技术支持合同 |
| 12 | access_rights | 访问权限 | 技术支持合同 |
| 13 | termination_support | 支持终止 | 技术支持合同 |

### 8.2 标准条款模板库

#### 赔偿条款 (Liability)
```
Supplier's total aggregate liability shall not exceed the total fees 
paid by Customer in the 12 months preceding the claim.
```

#### 知识产权 (IP)
```
Alauda retains all rights to the pre-existing platform (PaaS) and any 
derivative works based on its core technology. Customer owns only custom 
components developed specifically for Customer.
```

#### 验收条款 (Acceptance)
```
Deliverables are deemed accepted if no written rejection is received 
within 10 business days of delivery.
```

#### SLA 响应时间 (SLA Response)
```
Response times: P1 (Critical): 30 minutes initial response; P2 (High): 2 hours; 
P3 (Medium): 4 hours; P4 (Low): 8 hours. Resolution times 
to be determined on a best-effort basis.
```

#### 培训承诺 (Training Commitment)
```
Alauda will provide up to 40 hours of online training per year. Additional 
training may be purchased at agreed rates. Training content and schedule 
to be mutually agreed.
```

#### 支持期限 (Support Duration)
```
Warranty support is provided for the current major version and one prior 
major version, for a maximum of 18 months from general availability of 
the new major version.
```

#### 责任排除 (Exclusion of Liability)
```
In no event shall Alauda be liable for any indirect, incidental, special, 
consequential, or punitive damages, including without limitation loss of 
profits, data, use, or goodwill, regardless of the form of action.
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0 | 2025-03-03 | 初始版本，支持销售合同 6 个维度 |
| 2.0 | 2026-02-20 | 新增技术支持合同 7 个维度，支持多语言合同 |

---

## 联系支持

如有问题或建议，请联系法务团队或提交 Issue 到脚本仓库。

---

*本手册由 Alauda Global Legal Agent 自动生成辅助编写*
