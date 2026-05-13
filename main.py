"""
╔══════════════════════════════════════════════════════════════╗
║  看房AI Book — 专业房产评估与购房决策系统                    ║
║  Beijing Property Intelligence Platform                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from ui_components import (
    set_global_style,
    render_sidebar_v2,
    # Client mode tabs
    render_client_input,
    render_client_overview,
    render_client_valuation,
    render_client_investment,
    render_client_risk,
    render_client_report,
    # Admin mode tabs
    render_admin_database,
    render_admin_samples,
    render_admin_import,
    render_admin_params,
    render_admin_quality,
    render_admin_dashboard,
    # Legacy
    render_poster,
    render_report,
)

set_global_style()

# ══════════════════════════════════════════════════════════════
#  顶部导航
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div style="background:linear-gradient(135deg,#0F172A,#1E293B);padding:20px 28px;
            border-radius:12px;margin-bottom:4px">
    <div style="display:flex;align-items:center;gap:16px">
        <div>
            <div style="font-size:22px;font-weight:700;color:#FFFFFF;letter-spacing:2px">
                🏠 看房AI Book
            </div>
            <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-top:4px">
                专业房产评估与购房决策系统
            </div>
        </div>
        <div style="margin-left:auto;font-size:12px;color:rgba(255,255,255,0.35)">
            面向投资者与自住客户的客观购房评估报告工具
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  模式选择
# ══════════════════════════════════════════════════════════════

mode = st.sidebar.radio(
    "📍 工作模式",
    ["🏠 客户评估模式", "🔧 高级后台模式"],
    key="app_mode"
)

is_client = mode == "🏠 客户评估模式"

# ══════════════════════════════════════════════════════════════
#  客户评估模式
# ══════════════════════════════════════════════════════════════

if is_client:

    with st.sidebar:
        st.caption("👤 当前：客户评估模式")
    params = render_sidebar_v2()

    # 使用流程提示
    st.markdown("""
    <div style="display:flex;gap:12px;align-items:center;background:#F0F7FF;border-radius:8px;padding:12px 20px;margin-bottom:12px">
        <div style="background:#2563EB;color:#fff;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700">1</div>
        <span style="font-size:13px;color:#475569">填写房源信息</span>
        <span style="color:#CBD5E1">→</span>
        <div style="background:#2563EB;color:#fff;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700">2</div>
        <span style="font-size:13px;color:#475569">点击生成评估报告</span>
        <span style="color:#CBD5E1">→</span>
        <div style="background:#2563EB;color:#fff;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700">3</div>
        <span style="font-size:13px;color:#475569">查看估值结论与专业报告</span>
    </div>
    """, unsafe_allow_html=True)

    # 顶部操作区
    col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
    with col_b1:
        eval_btn = st.button("📊 生成评估报告", type="primary", use_container_width=True)
    with col_b2:
        poster_btn = st.button("🖼️ 生成海报", use_container_width=True)
    with col_b3:
        report_btn = st.button("📄 专业报告", use_container_width=True)

    st.divider()

    # 6 个标签页
    t_input, t_overview, t_valuation, t_invest, t_risk, t_report = st.tabs([
        "📝 房源输入", "📋 总览结论", "🧠 估值分析", "📈 投资测算", "⚠️ 风险分析", "📄 专业报告"
    ])

    with t_input:
        render_client_input(params)

    with t_overview:
        if eval_btn:
            render_client_overview(params)
        else:
            st.info("👈 填写房源参数后，点击「📊 生成评估报告」查看总览结论")

    with t_valuation:
        if eval_btn:
            render_client_valuation(params)
        else:
            st.info("👈 点击「📊 生成评估报告」查看估值分析")

    with t_invest:
        if eval_btn:
            render_client_investment(params)
        else:
            st.info("👈 点击「📊 生成评估报告」查看投资测算")

    with t_risk:
        if eval_btn:
            render_client_risk(params)
        else:
            st.info("👈 点击「📊 生成评估报告」查看风险分析")

    with t_report:
        render_client_report(params)

    # 顶部按钮处理
    if poster_btn:
        render_poster()
    if report_btn:
        render_report()

# ══════════════════════════════════════════════════════════════
#  高级后台模式
# ══════════════════════════════════════════════════════════════

else:
    st.sidebar.caption("🔒 当前：高级后台模式")

    t_db, t_samples, t_import, t_params, t_quality, t_dash = st.tabs([
        "🏘️ 小区数据库", "📊 成交样本库", "📥 数据导入",
        "⚙️ 模型参数", "✅ 数据质量", "📈 研究仪表盘"
    ])

    with t_db:
        render_admin_database()

    with t_samples:
        render_admin_samples()

    with t_import:
        render_admin_import()

    with t_params:
        render_admin_params()

    with t_quality:
        render_admin_quality()

    with t_dash:
        render_admin_dashboard()
