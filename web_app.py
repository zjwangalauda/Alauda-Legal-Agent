import os
import html
import logging
import streamlit as st
import tempfile
import zipfile
import shutil
from pathlib import Path

from alauda_legal_agent import extract_text_from_file, run_llm_inference, MAX_CONTRACT_CHARS
from docx_redline_engine import WordRedlineEngine

logger = logging.getLogger(__name__)

# 1. 页面级基础设置
st.set_page_config(
    page_title="Alauda Legal Agent | 灵雀云法务合规智能体",
    page_icon="Alauda brand/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"  # 强制展开侧边栏
)

# 2. 注入深度定制的 CSS (extracted to assets/theme.css — B1)
_css_path = os.path.join(os.path.dirname(__file__), "assets", "theme.css")
with open(_css_path) as _css_file:
    st.markdown(f"<style>{_css_file.read()}</style>", unsafe_allow_html=True)

# 3. 页面顶部 Hero Section
st.markdown("""
<div class="hero-container">
    <div style="background-color: transparent; height: 50px; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
        <img src="https://www.alauda.cn/Public/Home/images/new_header/logo_new_230524.png" style="height: 100%; object-fit: contain; filter: brightness(0) invert(1);">
    </div>
    <div>
        <h1 class="hero-title">Global Legal Agent</h1>
        <p class="hero-subtitle">V6.1 Semantic AI Edition · 专为企业级 SaaS/PaaS 商业模式打造的自动化合同审查大脑</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 侧边栏配置
with st.sidebar:
    st.markdown(
        "<div style='text-align: center; margin-bottom: 30px;'><img src='https://www.alauda.cn/Public/Home/images/new_header/logo_new_230524.png' width='180'></div>",
        unsafe_allow_html=True
    )
    st.info("💡 提示：使用键盘快捷键 `Cmd/Ctrl + .` 可以快速展开或收起本侧边栏。")
    st.markdown("### ⚙️ 引擎配置")
    model_provider = st.selectbox(
        "选择底层大模型引擎",
        ("Google Gemini (推荐)", "OpenAI", "Anthropic Claude", "第三方/私有兼容接口 (Custom)")
    )

    provider_map = {
        "Google Gemini (推荐)": "google",
        "OpenAI": "openai",
        "Anthropic Claude": "anthropic",
        "第三方/私有兼容接口 (Custom)": "openai" # Most custom APIs use OpenAI format
    }

    base_url = None
    if model_provider == "第三方/私有兼容接口 (Custom)":
        base_url = st.text_input("Base URL (必填)", placeholder="例如: https://api.deepseek.com/v1", help="提供商给您的API网页调用根地址")
        custom_model = st.text_input("Model ID (必填)", placeholder="例如: deepseek-chat", help="提供商给您的模型名称")
        if custom_model:
            provider_map["第三方/私有兼容接口 (Custom)"] = custom_model

    api_key = st.text_input("API Key (选填)", type="password", help="如不填写，系统将自动使用灵雀云内置的免费 AI 引擎")

    # 内置免费引擎回退逻辑
    using_builtin = False
    if not api_key:
        try:
            builtin_key = st.secrets.get("BUILTIN_API_KEY", "")
            builtin_url = st.secrets.get("BUILTIN_BASE_URL", "")
            builtin_model = st.secrets.get("BUILTIN_MODEL", "claude-opus-4-6")
            if builtin_key:
                api_key = builtin_key
                base_url = builtin_url
                model_provider = "第三方/私有兼容接口 (Custom)"
                provider_map["第三方/私有兼容接口 (Custom)"] = builtin_model
                using_builtin = True
                st.success("🎁 已启用灵雀云内置免费 AI 引擎 (Claude Opus 4.6)，可直接使用！")
            else:
                st.warning("⚠️ 未配置密钥，且内置引擎不可用。系统将运行在本地 Mock 演示模式。")
        except Exception as e:
            logger.warning("Failed to load builtin secrets: %s", e)
            st.warning("⚠️ 未配置密钥。系统将运行在本地 Mock 演示模式。")

    st.markdown("---")
    st.markdown("### 🎯 审核基线雷达")
    st.markdown("""
    <div style='background: white; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 0.9rem; color: #475569 !important;'>
        <div style='margin-bottom: 8px; color: #1E293B !important;'>🛡️ <b>双轨制赔偿</b> <br><span style='color: #64748B !important; font-size: 0.8rem;'>上限 12个月 / 排除数据兜底</span></div>
        <div style='margin-bottom: 8px; color: #1E293B !important;'>🛡️ <b>知识产权防御</b> <br><span style='color: #64748B !important; font-size: 0.8rem;'>平台底座及衍生品所有权保留</span></div>
        <div style='margin-bottom: 8px; color: #1E293B !important;'>🛡️ <b>默示验收机制</b> <br><span style='color: #64748B !important; font-size: 0.8rem;'>10 个工作日强制结项</span></div>
        <div style='margin-bottom: 8px; color: #1E293B !important;'>🛡️ <b>支持范围限缩</b> <br><span style='color: #64748B !important; font-size: 0.8rem;'>拒绝驻场 / 拒绝无边界定制</span></div>
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

    start_btn = False
    enable_redline = False
    if mode == "📄 单文档快速审计 (Single-Doc)":
        st.info("💡 适合处理单一的 Master Agreement、EULA 或 Order Form。支持 PDF, Word, TXT 格式。")
        uploaded_file = st.file_uploader("拖拽合同文件至此", type=['pdf', 'docx', 'txt'])

        # V6.1 Feature Toggle
        st.markdown("##### 🚀 高级选项 (Advanced Options)")
        enable_redline = st.checkbox("自动生成原生 Word 批注版 (.docx Track Changes)", value=True, help="如果勾选，系统将深入 Word 底层 AST，直接在原文件中打上红色修订标记和侧边栏法务批注。注意：仅对上传的 .docx 文件有效。")

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
            try:
                redlined_path = None
                if mode == "📄 单文档快速审计 (Single-Doc)":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    try:
                        text = extract_text_from_file(tmp_path)
                    except ValueError as e:
                        st.error(f"文件格式错误: {e}")
                        text = ""

                    if text:
                        if len(text) > MAX_CONTRACT_CHARS:
                            st.warning(f"文档内容超过 {MAX_CONTRACT_CHARS:,} 字符限制，将自动截断处理。")

                        report = run_llm_inference(text, "single", api_key, model_provider=provider_map[model_provider], base_url=base_url)

                        # V6.1 Native Redlining Logic
                        redlined_path = None
                        if enable_redline and report and tmp_path.lower().endswith('.docx') and hasattr(report, 'legal_reviews') and report.legal_reviews:
                            redlined_path = tmp_path.replace(".docx", "_redlined.docx")
                            try:
                                shutil.copy(tmp_path, redlined_path)
                                engine = WordRedlineEngine(redlined_path)
                                for rev in report.legal_reviews:
                                    engine.apply_redline(rev.original_text, rev.suggested_revision, f"[{rev.dimension}] \n{rev.rationale}")
                                engine.save(redlined_path)
                            except Exception as e:
                                logger.error("Redlining failed: %s", e)
                                redlined_path = None
                    else:
                        report = None

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
                                    try:
                                        content = extract_text_from_file(file_path)
                                    except ValueError as e:
                                        st.error(f"文件格式错误: {e}")
                                        content = ""
                                    if content:
                                        all_text += f"\n\n================ DOCUMENT: {file} ================\n\n"
                                        all_text += content

                        if all_text and len(all_text) > MAX_CONTRACT_CHARS:
                            st.warning(f"案卷内容超过 {MAX_CONTRACT_CHARS:,} 字符限制，将自动截断处理。")

                        report = run_llm_inference(all_text, "multi", api_key, model_provider=provider_map[model_provider], base_url=base_url)

                st.session_state['current_report'] = report
                st.session_state['redlined_path'] = redlined_path if mode == "📄 单文档快速审计 (Single-Doc)" else None
                st.session_state['report_mode'] = mode
            except Exception as e:
                logger.error("Processing failed: %s", e)
                st.error(f"处理失败: {e}")
                report = None

    # 独立于按钮点击的渲染模块，只要 session_state 里有数据就渲染
    report = st.session_state.get('current_report', None)
    redlined_path = st.session_state.get('redlined_path', None)
    render_mode = st.session_state.get('report_mode', mode)

    # 结果渲染
    # Security note (A15/P0 #1): All LLM output fields are escaped via html.escape()
    # to prevent XSS from untrusted contract content reflected through model responses.
    if report:
        st.success("🎯 综合审计决议已生成！")

        # 1. 渲染 CXO 视角
        st.markdown("### 👨‍💼 首席执行官群 (CXO) 审批台")
        cxo_color = "#16A34A" if "直接签约" in report.cxo_view.approval_recommendation else "#DC2626" if "拒签" in report.cxo_view.approval_recommendation else "#D97706"
        st.markdown(f"""
        <div style="background: white; border-top: 5px solid {cxo_color}; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px;">
            <h4 style="margin-top:0;">最终决议：<span style="color: {cxo_color};">{html.escape(report.cxo_view.approval_recommendation)}</span></h4>
            <p><b>💥 致命阻碍 (Deal Breakers):</b> {html.escape(report.cxo_view.deal_breaker_summary)}</p>
            <div style="background-color: #F1F5F9; padding: 15px; border-radius: 6px; border-left: 4px solid #94A3B8;">
                <b>💡 战略博弈指导 (Strategic Playbook):</b><br>
                <span style="color: #475569;">{html.escape(report.cxo_view.strategic_advice)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 渲染商务运营视角
        st.markdown("### 📈 运营与商务履约看板")
        st.info("以下核心要素已从错综复杂的长文本中自动提炼，供 PMO 与财务侧做履约及现金流测算。")
        comm_data = [{"核心要素": c.key_metric, "合同摘要": c.extracted_value, "运营影响测算": c.operational_impact} for c in report.commercial_summary]
        st.table(comm_data)
        st.markdown("---")

        # 3. 渲染法务视角
        st.markdown("### ⚖️ 法务合规与红线防御阵地")

        if render_mode != "📄 单文档快速审计 (Single-Doc)":
            st.markdown("#### 📚 案卷效力层级 (Document Hierarchy)")
            hierarchy_data = [{"层级 (Level)": f"Level {n.precedence_level}", "文档类型": n.doc_type, "文件名": n.doc_name} for n in sorted(report.document_hierarchy, key=lambda x: x.precedence_level)]
            st.table(hierarchy_data)
            st.markdown("#### 🚨 跨文档隐藏后门雷达")
        else:
            st.markdown("#### 🚨 合同红线风险审查矩阵")

        # 渲染具体的风险卡片
        items = getattr(report, 'hidden_backdoors', None) or getattr(report, 'legal_reviews', None)

        if not items:
            st.success("🎉 法务通关！未检测到任何突破商业红线的高危条款。")
        else:
            for item in items:
                # 单双模式字段兼容处理
                is_multi = hasattr(item, 'master_clause')

                dim = item.dimension
                risk_badge = '<span class="risk-badge-high">🔴 HIGH RISK</span>' if (not is_multi and item.risk_level == "HIGH") or is_multi else '<span class="risk-badge-medium">🟡 MEDIUM RISK</span>'
                card_class = "risk-high" if (not is_multi and item.risk_level == "HIGH") or is_multi else "risk-medium"

                html_card = f"""
                <div class="risk-card {card_class}">
                    <div class="risk-title">{html.escape(dim)} {risk_badge}</div>
                """

                if is_multi:
                    html_card += f'''
<div class="risk-section-title">🏰 主协议防线 (Master Defense)</div>
<div class="original-text">{html.escape(item.master_clause)}</div>
<div class="risk-section-title">🗡️ 越权攻击点 ({html.escape(item.source_doc)})</div>
<div class="original-text">{html.escape(item.overriding_clause)}</div>
<div class="risk-section-title">💡 致命风险溯源 (Risk Analysis)</div>
<div class="rationale-text">{html.escape(item.risk_analysis)}</div>
<div class="risk-section-title">✅ 法务强制拦截方案 (Suggested Action)</div>
<div class="revision-box">{html.escape(item.suggested_action)}</div>
'''
                else:
                    html_card += f'''
<div class="risk-section-title">❌ 风险原文摘录 (Original Text)</div>
<div class="original-text">{html.escape(item.original_text)}</div>
<div class="risk-section-title">💡 商业与法务推理 (Rationale)</div>
<div class="rationale-text">{html.escape(item.rationale)}</div>
'''
                    if item.suggested_revision:
                        html_card += f'''
<div class="risk-section-title">✅ 建议回改条款 (Redline)</div>
<div class="revision-box">{html.escape(item.suggested_revision)}</div>
'''

                html_card += "</div>"
                st.markdown(html_card, unsafe_allow_html=True)

        # Render Download Buttons at the bottom
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            report_name = report.contract_name if hasattr(report, 'contract_name') else report.project_name
            md_export = f"# {report_name} 综合审计决议报告\n\n"
            md_export += f"## 👨‍💼 CXO 审批建议\n- **决议**: {report.cxo_view.approval_recommendation}\n"
            md_export += f"- **致命阻碍**: {report.cxo_view.deal_breaker_summary}\n"
            md_export += f"- **战略指导**: {report.cxo_view.strategic_advice}\n\n---\n\n"
            md_export += "## 📈 商务运营核心要素\n"
            for c in report.commercial_summary:
                md_export += f"- **{c.key_metric}**: {c.extracted_value}\n  > 运营影响：{c.operational_impact}\n\n"
            md_export += "---\n\n## ⚖️ 法务风险审查\n\n"
            items = getattr(report, 'legal_reviews', None) or getattr(report, 'hidden_backdoors', None) or []
            for i, item in enumerate(items, 1):
                if hasattr(item, 'original_text'):
                    md_export += f"### {i}. {item.dimension} [{item.risk_level}]\n"
                    md_export += f"**原文**: {item.original_text}\n\n**分析**: {item.rationale}\n\n"
                    if item.suggested_revision:
                        md_export += f"**建议修改**: {item.suggested_revision}\n\n"
                else:
                    md_export += f"### {i}. {item.dimension}\n"
                    md_export += f"**主协议条款**: {item.master_clause}\n\n**越权条款 ({item.source_doc})**: {item.overriding_clause}\n\n"
                    md_export += f"**风险分析**: {item.risk_analysis}\n\n**拦截方案**: {item.suggested_action}\n\n"
                md_export += "---\n\n"
            st.download_button("⬇️ 导出审计报告 (.md)", data=md_export, file_name="review_report.md")

        if redlined_path and os.path.exists(redlined_path):
            with col_dl2:
                with open(redlined_path, "rb") as f:
                    st.download_button(
                        label="📝 下载原生批注版合同 (.docx)",
                        data=f,
                        file_name="Redlined_Contract.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
    elif start_btn:
        st.error("处理失败，请检查网络或确认文档内容是否有效。")

    if not st.session_state.get('current_report') and not start_btn:
        # 初始空白状态提示
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: white; border-radius: 12px; border: 1px dashed #CBD5E1; color: #94A3B8 !important;">
            <p style="font-size: 3rem; margin-bottom: 10px;">🛡️</p>
            <h3 style="color: #64748B !important;">等待案卷摄入</h3>
            <p style="color: #94A3B8 !important;">请在左侧上传文件并启动引擎。支持自动多模态解析及跨文档溯源。</p>
        </div>
        """, unsafe_allow_html=True)
