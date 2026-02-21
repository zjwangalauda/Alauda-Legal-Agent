import os
import sys
import glob
import json
import argparse
from typing import List, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# 1. AI 依赖装载与兜底机制 (Dependencies & Fallbacks)
# ---------------------------------------------------------
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.output_parsers import PydanticOutputParser
    has_langchain = True
except ImportError:
    has_langchain = False

def extract_text_from_file(file_path: str) -> str:
    """提取各种格式文档的纯文本"""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            import pypdf
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
        elif ext in ['.docx', '.doc']:
            from docx import Document
            doc = Document(file_path)
            for p in doc.paragraphs:
                if p.text.strip(): text += p.text.strip() + "\n"
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data: text += " | ".join(row_data) + "\n"
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
    except Exception as e:
        print(f"⚠️ 提取文件 {file_path} 失败: {e}")
    return text

# ---------------------------------------------------------
# 2. 结构化数据定义 (Data Schemas)
# ---------------------------------------------------------
# --- Single Doc Schema ---
class ClauseReview(BaseModel):
    dimension: str = Field(description="审查维度（如：订阅计量、赔偿条款、知识产权、验收条款、SLA响应时间、支持范围等）")
    original_text: str = Field(description="合同原文中触发风险的段落摘录 (需保留原英文)")
    risk_level: str = Field(description="风险等级：HIGH (高危红线), MEDIUM (中等风险)")
    rationale: str = Field(description="基于Alauda SaaS与开源商业逻辑的具体中文分析原因")
    suggested_revision: Optional[str] = Field(description="符合Alauda标准的英文条款改写建议。如果没有直接修改建议则为空。")

class ContractReviewReport(BaseModel):
    contract_name: str = Field(description="合同名称推断")
    overall_assessment: str = Field(description="合同整体风险评估总结 (中文，200字以内)")
    reviews: List[ClauseReview] = Field(description="识别出的中高风险条款列表，若无则为空")

# --- Multi-Doc Schema ---
class DocNode(BaseModel):
    doc_name: str = Field(description="文档名称")
    doc_type: str = Field(description="文档类型 (如: Master Agreement, SOW, Order Form, EULA)")
    precedence_level: int = Field(description="效力层级优先级 (1为最高优先级)")

class ConflictItem(BaseModel):
    dimension: str = Field(description="冲突维度 (如: 赔偿责任, 知识产权, 验收标准)")
    master_clause: str = Field(description="主协议中的保护性条款摘录")
    overriding_clause: str = Field(description="附件/SOW中的后门/推翻性条款摘录")
    source_doc: str = Field(description="包含后门条款的文档名称")
    risk_analysis: str = Field(description="该跨文档冲突导致的具体法务与商业风险分析")
    suggested_action: str = Field(description="处理建议 (如: 强制删除该条款，或在SOW中限定特殊责任上限)")

class MultiDocReviewReport(BaseModel):
    project_name: str = Field(description="项目或客户名称")
    document_hierarchy: List[DocNode] = Field(description="文档效力层级拓扑图")
    overall_assessment: str = Field(description="全局视角评估总结")
    hidden_backdoors: List[ConflictItem] = Field(description="跨文档冲突与隐藏后门列表")

# ---------------------------------------------------------
# 3. 系统提示词 (System Prompts)
# ---------------------------------------------------------
ALAUDA_BASELINE = """
# Alauda 核心商业红线 (Context)
Alauda 采用“底层开源 + 企业版按量订阅”的混合商业模式。你在审查合同时，必须坚守以下核心商业原则，这是公司的底线：
1. 订阅计量 (Subscription Metrics)：拒绝“企业级无限制 (Enterprise-wide)” 或“买断式(perpetual/unlimited)”使用权，授权必须基于具体的计量单位 (如 Node, Core, vCPU)。
2. 双轨制赔偿限额 (Liability Cap)：商业订阅坚守以“索赔前 12 个月内已付费用”为上限。免费版(EULA)上限不超过US$50。必须明确排除间接损失和数据丢失(data loss)的兜底责任。
3. 知识产权 (IP)：明确区分“定制成果”与“平台核心”。客户仅拥有定制部分，Alauda 必须保留核心 PaaS 平台及其衍生作品的所有权。
4. 交付与验收 (Acceptance)：拒绝无限循环拒收或单方面书面验收，必须带有 10 个工作日缓冲期的“默示验收 (Deemed Acceptance)”。
5. SLA 运营底线 (Support SLA)：响应时间不得短于运维团队的承受上限（Level 1 至少需 30 分钟，Level 2 需 2 小时，Level 3 需 4 小时）。拒绝 24/7 的无限制支持承诺。
6. 支持范围边界 (Support Scope)：拒绝“无限制兜底”。明确排除定制开发 (Custom code)、现场驻场支持 (On-site)，以及未经 Alauda 显式认证的第三方软件。
"""

SINGLE_DOC_PROMPT = f"""你是一名精通全球通用法律、开源软件合规性，以及企业级 SaaS/PaaS 商业订阅模式的资深法务与运营架构师。
{ALAUDA_BASELINE}
# 任务 (Task)
深入理解提供的单个合同文本，找出所有违反上述 6 大核心红线的条款，并输出标准化的JSON数据。
严格遵循输出格式。不要报告合规条款。

# 语言要求 (CRITICAL LANGUAGE REQUIREMENT)
1. 自动检测输入合同的语言。
2. 如果输入的合同主要是【中文】，那么所有输出字段（包括 rationale 和 suggested_revision）必须使用【中文】。
3. 如果输入的合同是【英文】或其他语言，那么 rationale 请使用中文解释，但 suggested_revision 必须使用专业的【Legal English】给出修正条款。
"""

MULTI_DOC_PROMPT = f"""你是一名精通复杂 B2B 软件采购流程的资深法务架构师。
目前你正在处理一组【互相关联的合同簇 (Contract Bundle)】。狡猾的客户常常会在低层级文件（如SOW、Order）中插入“优先权声明 (Order of Precedence)”推翻主合同底线。
{ALAUDA_BASELINE}
# 你的任务：
1. 阅读传入的所有关联文档内容。
2. 建立【文档效力层级拓扑图】：分析哪些文档在发生冲突时具有最高优先权。
3. 跨文档检索【隐藏后门】：对比主协议的保护性条款与附件/SOW中的特殊要求（如突破12个月赔偿、索取平台衍生IP）。
4. 严格按照提供的JSON结构输出您的跨文档冲突分析结果。

# 语言要求 (CRITICAL LANGUAGE REQUIREMENT)
1. 自动检测输入案卷的主要语言。
2. 如果案卷主要是【中文】，那么所有输出字段（包括 risk_analysis 和 suggested_action）必须使用【中文】。
3. 如果案卷是【英文】或其他语言，risk_analysis 请使用中文解释，但 suggested_action 必须使用专业的【Legal English】给出法务强制拦截条款。
"""

# ---------------------------------------------------------
# 4. 核心推理引擎 (AI Inference Engines)
# ---------------------------------------------------------
def run_llm_inference(text: str, mode: str, api_key: str):
    if not api_key or not has_langchain:
        print("⚠️ 未检测到有效 API Key 或 LangChain 环境。触发本地大模型 Mock 模式...")
        return get_mock_response(mode)

    parser = PydanticOutputParser(pydantic_object=ContractReviewReport if mode == "single" else MultiDocReviewReport)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SINGLE_DOC_PROMPT if mode == "single" else MULTI_DOC_PROMPT),
        ("user", "【需审核的合同数据】\n{contract_text}\n\n请严格按照以下JSON格式输出审核结果：\n{format_instructions}")
    ])
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1, max_output_tokens=8192, google_api_key=api_key)
    chain = prompt | llm | parser
    
    print(f"⏳ 正在调用 Gemini 1.5 Pro 进行深度 {'单文档语义分析' if mode == 'single' else '多文档图谱交叉审查'}...")
    try:
        return chain.invoke({"contract_text": text[:500000], "format_instructions": parser.get_format_instructions()})
    except Exception as e:
        print(f"❌ API 调用或解析失败: {e}")
        return None

def get_mock_response(mode: str):
    """Fallback Mock Responses to guarantee out-of-the-box demo capabilities"""
    if mode == "single":
        return ContractReviewReport(
            contract_name="Standard Software Trial Agreement",
            overall_assessment="系统执行了降级Mock分析。这是一份示例评估。发现客户尝试突破12个月赔偿上限并规避默示验收。",
            reviews=[
                ClauseReview(
                    dimension="验收条款 (Acceptance)",
                    original_text="Deliverables shall not be deemed accepted until Bank issues a formal Final Acceptance Certificate in writing.",
                    risk_level="MEDIUM",
                    rationale="排除了默示验收，会严重拖延SaaS业务的尾款结算。",
                    suggested_revision="Bank shall carry out Acceptance Tests within 10 business days. Deliverables are deemed accepted if no written rejection is received within this 10-day period."
                )
            ]
        )
    else:
        return MultiDocReviewReport(
            project_name="MegaBank 核心数据迁移与平台采购 (Multi-Doc Mock)",
            overall_assessment="系统执行了跨文档拓扑分析Mock。客户利用实施团队在 SOW(附件) 中的审核盲区，强行植入了『优先级覆盖』并设定了『无限数据兜底责任』。",
            document_hierarchy=[
                DocNode(doc_name="2_SOW_Phase1.docx", doc_type="SOW", precedence_level=1),
                DocNode(doc_name="1_Master_Agreement_GFA.pdf", doc_type="Master Agreement", precedence_level=2)
            ],
            hidden_backdoors=[
                ConflictItem(
                    dimension="赔偿责任上限突破 & 数据丢失无限兜底",
                    master_clause="GFA 14.1: The total liability... shall not exceed fees paid in 12 months.",
                    overriding_clause="SOW 5.2: Supplier agrees that Liability cap in GFA 14.1 shall not apply. Supplier shall be fully liable for data loss.",
                    source_doc="2_SOW_Phase1.docx",
                    risk_analysis="⚠️ 致命级隐藏后门！客户利用 SOW 中的优先权覆盖条款，成功在实施附件中推翻了主协议的防线，导致无上限索赔敞口。",
                    suggested_action="法务介入强制拦截：删除 SOW Section 5.2。并在 SOW 中重申主协议赔偿上限绝对适用。"
                )
            ]
        )

# ---------------------------------------------------------
# 5. 报告渲染器 (Report Renderers)
# ---------------------------------------------------------
def render_single_doc_report(report: ContractReviewReport, output_file: str):
    md = f"# 🚀 Alauda AI Legal Agent (V4 Ultimate) 单文档审核报告\n\n"
    md += f"> **合同名称**: {report.contract_name}\n"
    md += f"> **审计引擎**: Gemini (Semantic Reasoning)\n\n"
    md += f"## 📝 整体评估\n{report.overall_assessment}\n\n"
    md += "## 📊 深度语义审查矩阵\n\n"
    if not report.reviews: md += "🎉 **未检测到明显高/中级别风险条款。**\n\n"
    for i, rev in enumerate(report.reviews, 1):
        icon = "🔴" if rev.risk_level.upper() == "HIGH" else "🟡"
        md += f"### {i}. {rev.dimension} {icon} {rev.risk_level}\n"
        md += f"**❌ 风险定位 (Original)**:\n> {rev.original_text}\n\n"
        md += f"**💡 推理逻辑 (Rationale)**:\n{rev.rationale}\n\n"
        if rev.suggested_revision: md += f"**✅ 推荐回改 (Suggested Revision)**:\n```text\n{rev.suggested_revision}\n```\n\n"
        md += "---\n\n"
    with open(output_file, "w", encoding="utf-8") as f: f.write(md)

def render_multi_doc_report(report: MultiDocReviewReport, output_file: str):
    md = f"# 🕸️ Alauda AI Legal Agent (V4 Ultimate) 跨文档审计报告\n\n"
    md += f"> **审计案列**: {report.project_name}\n"
    md += f"> **审计引擎**: Gemini (Knowledge Graph & Cross-reference)\n\n"
    md += f"## 📝 案卷全景总结\n{report.overall_assessment}\n\n"
    md += "## 📚 文档效力拓扑图 (Document Hierarchy)\n"
    md += "> *注意：层级 1 (Level 1) 代表发生条款冲突时的最高解释权。*\n\n"
    md += "| 效力层级 | 文档类型 | 文档名称 |\n| :---: | :--- | :--- |\n"
    for node in sorted(report.document_hierarchy, key=lambda x: x.precedence_level):
        md += f"| **Level {node.precedence_level}** | {node.doc_type} | `{node.doc_name}` |\n"
    md += "\n## 🚨 跨文档隐藏后门雷达 (Hidden Backdoor Detections)\n\n"
    if not report.hidden_backdoors: md += "🎉 **完美！** 附属文档未推翻主协议红线。\n\n"
    for i, item in enumerate(report.hidden_backdoors, 1):
        md += f"### 💥 发现后门 #{i}：{item.dimension}\n"
        md += f"- **🏰 主协议防线**:\n  > {item.master_clause}\n\n"
        md += f"- **🗡️ 越权覆盖点 (`{item.source_doc}`)**:\n  > {item.overriding_clause}\n\n"
        md += f"**💡 致命风险溯源**:\n{item.risk_analysis}\n\n"
        md += f"**✅ 法务强拆建议**:\n```text\n{item.suggested_action}\n```\n\n---\n\n"
    with open(output_file, "w", encoding="utf-8") as f: f.write(md)

# ---------------------------------------------------------
# 6. 主执行入口 (Main CLI)
# ---------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alauda Ultimate AI Legal Agent (V4)")
    parser.add_argument("-f", "--file", help="[单文档模式] 要审查的文件路径 (.txt, .md, .pdf, .docx)")
    parser.add_argument("-d", "--dir", help="[多文档模式] 包含一组关联合同的目录，执行跨文档知识图谱关联审计")
    parser.add_argument("-o", "--output", default="ai_review_report.md", help="输出的Markdown报告路径")
    parser.add_argument("-k", "--key", help="Google Gemini API Key", default=os.getenv("GEMINI_API_KEY"))
    parser.add_argument("--process-json", help="Directly ingest JSON via stdin", action="store_true")
    
    args = parser.parse_args()
    
    if args.process_json:
        data = json.loads(sys.stdin.read())
        if "document_hierarchy" in data:
            render_multi_doc_report(MultiDocReviewReport(**data), args.output)
        else:
            render_single_doc_report(ContractReviewReport(**data), args.output)
        print(f"✅ 从 JSON 渲染报告成功: {args.output}")
        exit(0)
        
    if args.dir:
        # Multi-doc mode
        all_text = ""
        for file_path in glob.glob(os.path.join(args.dir, "*.*")):
            if os.path.isfile(file_path):
                content = extract_text_from_file(file_path)
                if content:
                    all_text += f"\n\n================ DOCUMENT: {os.path.basename(file_path)} ================\n\n"
                    all_text += content
        report = run_llm_inference(all_text, "multi", args.key)
        if report: 
            render_multi_doc_report(report, args.output)
            print(f"✅ 多文档关联审计完成: {args.output}")
            
    elif args.file:
        # Single doc mode
        text = extract_text_from_file(args.file)
        if not text:
            print("❌ 无法读取文件文本")
            exit(1)
        report = run_llm_inference(text, "single", args.key)
        if report: 
            render_single_doc_report(report, args.output)
            print(f"✅ 单文档智能审计完成: {args.output}")
            
    else:
        print("💡 Alauda AI Legal Agent (V4 Ultimate)")
        print("请选择工作模式：")
        print("  1. 单文档分析: python3 alauda_legal_agent.py -f contract.pdf")
        print("  2. 多文档关联: python3 alauda_legal_agent.py -d ./contract_bundle_dir/")
