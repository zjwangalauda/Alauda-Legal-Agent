import os
import streamlit as st
import tempfile
import zipfile
import shutil
from pathlib import Path

# Import our core agent logic
from alauda_legal_agent import extract_text_from_file, run_llm_inference

# Configure Streamlit page
st.set_page_config(
    page_title="Alauda Legal Agent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Alauda branding
st.markdown("""
<style>
    :root {
        --alauda-blue: #3BAEE4;
        --alauda-navy: #0F2B46;
    }
    .stApp {
        background-color: #F8FAFC;
    }
    .main-header {
        color: #1A6A9A;
        border-bottom: 3px solid #3BAEE4;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #3BAEE4;
        color: white;
        border: none;
        border-radius: 4px;
    }
    .stButton>button:hover {
        background-color: #2A8ABF;
        color: white;
    }
    .risk-high {
        background-color: #FEE2E2;
        border-left: 5px solid #DC2626;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .risk-medium {
        background-color: #FEF9C3;
        border-left: 5px solid #EAB308;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .revision-box {
        background-color: #EAF6FC;
        padding: 15px;
        border-radius: 4px;
        font-family: monospace;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://www.alauda.cn/upload/portal/20211231/e15647dd84fba1e9eb7720235d648dd2.png", width=200) # Fallback placeholder
    st.markdown("### ⚙️ 系统配置")
    api_key = st.text_input("Google Gemini API Key", type="password", help="输入您的 API Key 以激活语义推理引擎")
    
    st.markdown("---")
    st.markdown("### 📑 审核模式")
    mode = st.radio(
        "选择分析模式",
        ("单文档快速扫描", "多文档防后门审计 (推荐)")
    )
    
    st.markdown("---")
    st.markdown("### 💡 核心红线")
    st.info("1. 12个月赔偿上限\n2. 拒绝衍生品IP买断\n3. 10天默示验收\n4. 拒绝数据无上限兜底\n5. 拒绝驻场及定制代码")

# Main Content
st.markdown('<h1 class="main-header">🚀 Alauda Global Legal Agent (V4)</h1>', unsafe_allow_html=True)
st.markdown("欢迎使用 Alauda 法务合规智能体。请上传客户发送的合同原件（支持 PDF/DOCX/TXT）。")

if mode == "单文档快速扫描":
    uploaded_file = st.file_uploader("📎 上传单份合同文件", type=['pdf', 'docx', 'txt'])
    
    if st.button("开始智能审计 🔍", disabled=not uploaded_file):
        if not api_key:
            st.error("请先在左侧侧边栏配置 Gemini API Key！")
        else:
            with st.spinner("⏳ 正在提取文本并呼叫 Gemini 1.5 Pro 进行百万上下文推理..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Extract and analyze
                text = extract_text_from_file(tmp_path)
                report = run_llm_inference(text, "single", api_key)
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                if report:
                    st.success("✅ 审计完成！")
                    st.markdown(f"### 📋 案卷总结")
                    st.write(report.overall_assessment)
                    
                    st.markdown("### 🚨 风险矩阵")
                    if not report.reviews:
                        st.balloons()
                        st.success("未检测到明显违反 SaaS 商业红线的高危条款！")
                    else:
                        for rev in report.reviews:
                            risk_class = "risk-high" if rev.risk_level == "HIGH" else "risk-medium"
                            icon = "🔴" if rev.risk_level == "HIGH" else "🟡"
                            
                            st.markdown(f"""
                            <div class="{risk_class}">
                                <h4>{icon} {rev.dimension}</h4>
                                <b>❌ 原文摘录:</b><br><i>{rev.original_text}</i><br><br>
                                <b>💡 业务推理逻辑:</b><br>{rev.rationale}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if rev.suggested_revision:
                                st.markdown("<b>✅ 推荐 Legal English 回改方案:</b>", unsafe_allow_html=True)
                                st.markdown(f'<div class="revision-box">{rev.suggested_revision}</div>', unsafe_allow_html=True)
                                
                    # Provide Markdown download
                    md_export = f"# {report.contract_name} 审核报告\n\n{report.overall_assessment}"
                    st.download_button("⬇️ 导出审计报告 (.md)", data=md_export, file_name="review_report.md")
                else:
                    st.error("分析失败，请检查网络或 API Key 额度。")

else: # 多文档模式
    uploaded_file = st.file_uploader("🗂️ 上传合同案卷压缩包 (.zip)", type=['zip'], help="请将主协议、SOW、订单等文件打包为一个 ZIP 文件上传")
    
    if st.button("构建拓扑图并执行关联审计 🕸️", disabled=not uploaded_file):
        if not api_key:
            st.error("请先在左侧侧边栏配置 Gemini API Key！")
        else:
            with st.spinner("⏳ 正在解压案卷，构建效力拓扑图并嗅探跨文档后门..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save and extract zip
                    zip_path = os.path.join(temp_dir, "bundle.zip")
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    extract_dir = os.path.join(temp_dir, "extracted")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    # Read all files
                    all_text = ""
                    for root, _, files in os.walk(extract_dir):
                        for file in files:
                            if file.endswith(('.pdf', '.docx', '.txt')):
                                file_path = os.path.join(root, file)
                                content = extract_text_from_file(file_path)
                                if content:
                                    all_text += f"\n\n================ DOCUMENT: {file} ================\n\n"
                                    all_text += content
                    
                    report = run_llm_inference(all_text, "multi", api_key)
                    
                    if report:
                        st.success("✅ 跨文档关联审计完成！")
                        st.markdown(f"### 📋 案卷全景总结")
                        st.write(report.overall_assessment)
                        
                        st.markdown("### 📚 文档效力拓扑图")
                        # Construct a table for hierarchy
                        st.table([{"Level": node.precedence_level, "Type": node.doc_type, "Filename": node.doc_name} 
                                 for node in sorted(report.document_hierarchy, key=lambda x: x.precedence_level)])
                        
                        st.markdown("### 🚨 跨文档隐藏后门雷达")
                        if not report.hidden_backdoors:
                            st.balloons()
                            st.success("完美！附属文档未发现推翻主协议红线的后门条款。")
                        else:
                            for item in report.hidden_backdoors:
                                st.markdown(f"""
                                <div class="risk-high">
                                    <h4>💥 {item.dimension}</h4>
                                    <b>🏰 主协议防线:</b><br><i>{item.master_clause}</i><br><br>
                                    <b>🗡️ 越权覆盖点 ({item.source_doc}):</b><br><i>{item.overriding_clause}</i><br><br>
                                    <b>💡 致命风险溯源:</b><br>{item.risk_analysis}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown("<b>✅ 法务定向爆破方案:</b>", unsafe_allow_html=True)
                                st.markdown(f'<div class="revision-box">{item.suggested_action}</div>', unsafe_allow_html=True)
                    else:
                        st.error("分析失败，请检查压缩包内容或 API Key。")

