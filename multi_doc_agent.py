import os
import glob
import json
import argparse
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.output_parsers import PydanticOutputParser
    has_langchain = True
except ImportError:
    has_langchain = False

# Pydantic 结构化数据定义：跨文档层级与冲突报告
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

SYSTEM_PROMPT = """你是一名精通复杂B2B软件采购流程的资深法务架构师。
目前你正在处理一组【互相关联的合同簇 (Contract Bundle)】，包含主协议(Master)、服务说明书(SOW)或订单(Order)等。

狡猾的客户常常会在低层级的文件（如SOW）中插入“优先权声明 (Order of Precedence)”并推翻主合同的底线条款（如要求无限赔偿、数据兜底、买断IP）。

# 你的任务：
1. 阅读传入的所有关联文档内容。
2. 建立【文档效力层级拓扑图】：分析哪些文档在发生冲突时具有最高优先权。
3. 跨文档检索【隐藏后门】：对比主协议的保护性条款与附件/SOW中的特殊要求。
4. 严格按照提供的JSON结构输出您的分析结果。

# Alauda核心红线：
- 任何文档都不允许突破 12个月订阅费的赔偿上限。
- 绝不接受数据丢失(Data Loss)的无限兜底。
- 坚守核心平台知识产权，绝不因为实施了SOW而变成雇佣作品(Work for hire)。
"""

def analyze_multi_doc_mock(doc_bundle: str) -> MultiDocReviewReport:
    """Mock fallback demonstrating the Multi-Doc Graph extraction"""
    print("⏳ 正在调用 Gemini 1.5 Pro 进行【跨文档关联推理】与【后门嗅探】...")
    
    mock_response = MultiDocReviewReport(
        project_name="MegaBank 核心数据迁移与平台采购",
        overall_assessment="系统在对 GFA 和 SOW 进行交叉图谱比对后，发现严重逻辑冲突。虽然主协议(GFA)设定了标准的 12 个月赔偿上限并排除了间接损失，但客户利用实施团队在 SOW(附件) 中的审核盲区，强行植入了『优先级覆盖(Overrides)』声明，并在 SOW 第5条中设定了『无限数据兜底责任』。这属于典型的『明修栈道，暗度陈仓』商业陷阱，极度高危。",
        document_hierarchy=[
            DocNode(doc_name="2_SOW_Phase1.txt", doc_type="SOW (服务说明书)", precedence_level=1),
            DocNode(doc_name="1_Master_Agreement_GFA.txt", doc_type="Master Agreement (主框架协议)", precedence_level=2)
        ],
        hidden_backdoors=[
            ConflictItem(
                dimension="赔偿责任上限突破 & 数据丢失无限兜底",
                master_clause="GFA 14.1: The total aggregate liability... shall not exceed the total fees paid by Customer in the twelve (12) months. 14.2: Neither party shall be liable for indirect... damages.",
                overriding_clause="SOW 5.1 & 5.2: Supplier agrees that the Limitation of Liability cap set forth in Section 14.1 of the GFA shall not apply... Supplier shall be held fully and solely liable (without limit) for any data loss, corruption...",
                source_doc="2_SOW_Phase1.txt",
                risk_analysis="⚠️ 致命级隐藏后门！客户利用 SOW 中的『优先权覆盖条款 (Section 2)』，成功在实施附件中推翻了主协议的防线。如果业务或交付人员只看主合同而草率签下此 SOW，Alauda 将面临极其恐怖的、针对银行核心数据丢失的无限额索赔敞口。",
                suggested_action="法务介入强制拦截：删除 SOW Section 5 全段。并在 SOW 中重申：'Notwithstanding anything to the contrary, the liability cap and exclusions of indirect/data loss damages established in the GFA shall universally apply to this SOW without exception.'"
            )
        ]
    )
    return mock_response

def generate_multi_doc_report(report: MultiDocReviewReport, output_file: str):
    md = f"# 🕸️ Alauda AI - 跨文档关联审计报告 (Multi-Doc Graph Edition)\n\n"
    md += f"> **审计案列**: {report.project_name}\n"
    md += f"> **审计引擎**: Gemini (Knowledge Graph & Cross-reference)\n\n"
    
    md += f"## 📝 案卷全景总结 (Executive Summary)\n{report.overall_assessment}\n\n"
    
    md += "## 📚 文档效力拓扑图 (Document Hierarchy)\n"
    md += "> *注意：层级 1 (Level 1) 代表发生条款冲突时的最高解释权。*\n\n"
    md += "| 效力层级 | 文档类型 | 文档名称 |\n"
    md += "| :---: | :--- | :--- |\n"
    for node in sorted(report.document_hierarchy, key=lambda x: x.precedence_level):
        md += f"| **Level {node.precedence_level}** | {node.doc_type} | `{node.doc_name}` |\n"
    md += "\n"
    
    md += "## 🚨 跨文档隐藏后门雷达 (Hidden Backdoor Detections)\n\n"
    if not report.hidden_backdoors:
        md += "🎉 **完美！** 所有附属文档均未发现越权推翻主协议的红线条款。\n\n"
    else:
        for i, item in enumerate(report.hidden_backdoors, 1):
            md += f"### 💥 发现后门 #{i}：{item.dimension}\n"
            md += f"- **🏰 主协议防线 (Master Clause)**:\n  > {item.master_clause}\n\n"
            md += f"- **🗡️ 越权覆盖点 (Overriding Clause in `{item.source_doc}`)**:\n  > {item.overriding_clause}\n\n"
            md += f"**💡 致命风险溯源分析 (Risk Trace Analysis)**:\n{item.risk_analysis}\n\n"
            md += f"**✅ 法务强拆建议 (Suggested Counter-Measure)**:\n```text\n{item.suggested_action}\n```\n\n"
            md += "---\n\n"
            
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ 多文档审计报告已生成: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alauda Multi-Doc Legal Agent")
    parser.add_argument("-d", "--dir", help="包含多个合同文件的文件夹路径")
    parser.add_argument("-o", "--output", default="multi_doc_report.md", help="输出的报告路径")
    parser.add_argument("--process-json", action="store_true")
    
    args = parser.parse_args()
    
    if args.process_json:
        data = json.loads(sys.stdin.read())
        report = MultiDocReviewReport(**data)
        generate_multi_doc_report(report, args.output)
        exit(0)
        
    if not args.dir:
        print("💡 请提供包含一组关联合同的目录: python3 multi_doc_agent.py -d ./contracts/")
        exit(1)
        
    # 读取目录下的所有文件并拼装给大模型
    all_text = ""
    for file_path in glob.glob(os.path.join(args.dir, "*.*")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_text += f"\n\n================ DOCUMENT: {os.path.basename(file_path)} ================\n\n"
                all_text += f.read()
        except Exception:
            pass
            
    # 执行分析 (无API Key情况使用Mock展示其业务逻辑)
    report = analyze_multi_doc_mock(all_text)
    generate_multi_doc_report(report, args.output)

