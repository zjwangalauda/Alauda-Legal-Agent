import os
import streamlit as st
import tempfile
import zipfile
import shutil
from pathlib import Path

from alauda_legal_agent import extract_text_from_file, run_llm_inference

# 1. 页面级基础设置
st.set_page_config(
    page_title="Alauda Legal Agent | 灵雀云法务合规智能体",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 注入深度定制的 CSS (对标 Alauda 官网企业级视觉设计)
st.markdown("""
<style>
    /* 全局背景与字体 */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    
    /* 隐藏 Streamlit 默认的 Header 和 Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 顶部导航栏 / Hero Section 样式 */
    .hero-container {
        background: linear-gradient(135deg, #0F2B46 0%, #1A6A9A 100%);
        padding: 40px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .hero-logo {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        height: 60px;
        object-fit: contain;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #EAF6FC;
        margin-top: 5px;
        opacity: 0.9;
    }

    /* 上传区块美化 */
    .css-1n76uvr, .css-1y4p8pa {
        background-color: white;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 30px;
    }

    /* 主按钮美化 */
    .stButton>button {
        background-color: #3BAEE4;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 6px rgba(59, 174, 228, 0.2);
    }
    .stButton>button:hover {
        background-color: #2A8ABF;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 174, 228, 0.3);
    }

    /* 风险卡片样式设计 */
    .risk-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    .risk-high {
        border-left: 6px solid #EF4444; /* Tailwind Red 500 */
    }
    .risk-medium {
        border-left: 6px solid #F59E0B; /* Tailwind Yellow 500 */
    }
    
    .risk-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .risk-badge-high {
        background: #FEE2E2; color: #DC2626; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;
    }
    .risk-badge-medium {
        background: #FEF3C7; color: #D97706; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;
    }

    .risk-section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 8px;
    }
    .original-text {
        background-color: #F8FAFC;
        color: #475569;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        font-size: 0.9rem;
    }
    .rationale-text {
        color: #334155;
        line-height: 1.6;
    }
    .revision-box {
        background-color: #F0FDF4; /* Green tint for solution */
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 16px;
        border-radius: 8px;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 0.95rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 页面顶部 Hero Section
st.markdown("""
<div class="hero-container">
    <img src="https://www.alauda.cn/images/v2/logo-dark.svg" class="hero-logo" alt="Alauda Logo">
    <div>
        <h1 class="hero-title">Global Legal Agent</h1>
        <p class="hero-subtitle">V4 Semantic AI Edition · 专为企业级 SaaS/PaaS 商业模式打造的自动化合同审查大脑</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 侧边栏配置
with st.sidebar:
    st.image("https://www.alauda.cn/images/v2/logo-dark.svg", width=150)
    st.markdown("---")
    st.markdown("### ⚙️ 引擎配置")
    api_key = st.text_input("Gemini Pro API Key", type="password", help="请提供您的密钥以激活底层的百万上下文推理引擎。")
    if not api_key:
        st.warning("⚠️ 未配置密钥。系统将运行在本地 Mock 演示模式。")
    
    st.markdown("---")
    st.markdown("### 🎯 审核基线雷达")
    st.markdown("""
    <div style='background: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 0.9rem; color: #475569;'>
        <div style='margin-bottom: 8px;'>🛡️ <b>双轨制赔偿</b> <br><span style='color: #94A3B8; font-size: 0.8rem;'>上限 12个月 / 排除数据兜底</span></div>
        <div style='margin-bottom: 8px;'>🛡️ <b>知识产权防御</b> <br><span style='color: #94A3B8; font-size: 0.8rem;'>平台底座及衍生品所有权保留</span></div>
        <div style='margin-bottom: 8px;'>🛡️ <b>默示验收机制</b> <br><span style='color: #94A3B8; font-size: 0.8rem;'>10 个工作日强制结项</span></div>
        <div style='margin-bottom: 8px;'>🛡️ <b>支持范围限缩</b> <br><span style='color: #94A3B8; font-size: 0.8rem;'>拒绝驻场 / 拒绝无边界定制</span></div>
    </div>
    """, unsafe_allow_html=True)

# 5. 主工作区布局
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📁 提交案卷")
    mode = st.radio(
        "请选择智能审计模式：",
        ("📄 单文档快速审计 (Single-Doc)", "🗂️ 全案卷交叉审计 (Multi-Doc)")
    )
    
    if mode == "📄 单文档快速审计 (Single-Doc)":
        st.info("💡 适合处理单一的 Master Agreement、EULA 或 Order Form。支持 PDF, Word, TXT 格式。")
        uploaded_file = st.file_uploader("拖拽合同文件至此", type=['pdf', 'docx', 'txt'])
        start_btn = st.button("开始深度语义扫描 ⚡")
    else:
        st.info("💡 适合处理包含附件的大型采购案。系统将自动构建文档效力拓扑，探测高级别附件对主框架的越权覆盖。请上传 ZIP 压缩包。")
        uploaded_file = st.file_uploader("拖拽案卷压缩包至此 (.zip)", type=['zip'])
        start_btn = st.button("构建拓扑并开始探测 🕸️")

with col2:
    st.markdown("### 📊 审计看板")
    
    if start_btn and uploaded_file:
        with st.spinner("⏳ 正在唤醒大模型引擎..."):
            
            # 临时沙盒处理
            if mode == "📄 单文档快速审计 (Single-Doc)":
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                text = extract_text_from_file(tmp_path)
                report = run_llm_inference(text, "single", api_key)
                os.unlink(tmp_path)
                
            else:
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_path = os.path.join(temp_dir, "bundle.zip")
                    with open(zip_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    extract_dir = os.path.join(temp_dir, "extracted")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
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

        # 结果渲染
        if report:
            # 执行成功提示
            st.success("审计完成！报告已生成。")
            
            # 渲染摘要
            st.markdown("#### 📝 Executive Summary (全局视角)")
            st.write(report.overall_assessment)
            
            # 多文档特有：拓扑图
            if mode != "📄 单文档快速审计 (Single-Doc)":
                st.markdown("#### 📚 Document Hierarchy (效力拓扑)")
                hierarchy_data = [{"层级 (Level)": f"Level {n.precedence_level}", "文档类型": n.doc_type, "文件名": n.doc_name} for n in sorted(report.document_hierarchy, key=lambda x: x.precedence_level)]
                st.table(hierarchy_data)
                st.markdown("#### 🚨 Hidden Backdoors (隐藏后门雷达)")
            else:
                st.markdown("#### 🚨 Semantic Risk Matrix (语义风险矩阵)")

            # 渲染具体的风险卡片
            items = getattr(report, 'hidden_backdoors', None) or getattr(report, 'reviews', None)
            
            if not items:
                st.info("🎉 完美！未检测到任何突破商业红线的高危条款。可以安全放行。")
            else:
                for item in items:
                    # 单双模式字段兼容处理
                    is_multi = hasattr(item, 'master_clause')
                    
                    dim = item.dimension
                    risk_badge = '<span class="risk-badge-high">🔴 HIGH RISK</span>' if (not is_multi and item.risk_level == "HIGH") or is_multi else '<span class="risk-badge-medium">🟡 MEDIUM RISK</span>'
                    card_class = "risk-high" if (not is_multi and item.risk_level == "HIGH") or is_multi else "risk-medium"
                    
                    html_card = f"""
                    <div class="risk-card {card_class}">
                        <div class="risk-title">{dim} {risk_badge}</div>
                    """
                    
                    if is_multi:
                        html_card += f"""
                        <div class="risk-section-title">🏰 主协议防线 (Master Defense)</div>
                        <div class="original-text">{item.master_clause}</div>
                        <div class="risk-section-title">🗡️ 越权攻击点 ({item.source_doc})</div>
                        <div class="original-text">{item.overriding_clause}</div>
                        <div class="risk-section-title">💡 致命风险溯源 (Risk Analysis)</div>
                        <div class="rationale-text">{item.risk_analysis}</div>
                        <div class="risk-section-title">✅ 法务强制拦截方案 (Suggested Action)</div>
                        <div class="revision-box">{item.suggested_action}</div>
                        """
                    else:
                        html_card += f"""
                        <div class="risk-section-title">❌ 风险原文摘录 (Original Text)</div>
                        <div class="original-text">{item.original_text}</div>
                        <div class="risk-section-title">💡 商业与法务推理 (Rationale)</div>
                        <div class="rationale-text">{item.rationale}</div>
                        """
                        if item.suggested_revision:
                            html_card += f"""
                            <div class="risk-section-title">✅ Legal English 建议回改条款 (Redline)</div>
                            <div class="revision-box">{item.suggested_revision}</div>
                            """
                    
                    html_card += "</div>"
                    st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.error("处理失败，请检查网络或确认文档内容是否有效。")

    elif not start_btn:
        # 初始空白状态提示
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: white; border-radius: 12px; border: 1px dashed #CBD5E1; color: #94A3B8;">
            <p style="font-size: 3rem; margin-bottom: 10px;">🛡️</p>
            <h3>等待案卷摄入</h3>
            <p>请在左侧上传文件并启动引擎。支持自动多模态解析及跨文档溯源。</p>
        </div>
        """, unsafe_allow_html=True)
