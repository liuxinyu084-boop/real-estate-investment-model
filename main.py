"""
╔══════════════════════════════════════════════════════════════╗
║  看房AI Book — 专业房产评估与购房决策系统                    ║
║  Beijing Property Intelligence Platform                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from datetime import datetime
import time
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
        if st.button("📊 生成评估报告", type="primary", use_container_width=True, key="gen_report_btn"):
            st.session_state["report_generated"] = True
            st.session_state["report_generated_at"] = datetime.now().strftime("%m-%d %H:%M")
            st.session_state["client_active_tab"] = "📋 总览结论"
            st.success("✅ 评估报告已生成，正在跳转到总览结论...")
            time.sleep(0.5)
            st.rerun()
    with col_b2:
        poster_btn = st.button("🖼️ 生成海报", use_container_width=True)
    with col_b3:
        report_btn = st.button("📄 专业报告", use_container_width=True)

    st.divider()

    # 报告生成后的状态栏
    if st.session_state.get("report_generated"):
        comm = st.session_state.get("community", "—")
        dist = st.session_state.get("district", "—")
        area = st.session_state.get("area", 90)
        price = st.session_state.get("total_price", "—")
        gen_time = st.session_state.get("report_generated_at", "—")
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;padding:8px 16px;margin-bottom:8px;font-size:13px;color:#166534">
            📋 当前报告：{comm} ｜ {dist} ｜ {area}㎡ ｜ {price}万 ｜ 生成 {gen_time}
        </div>
        """, unsafe_allow_html=True)

    # 客户标签页（radio 控制切换）
    tab_options = ["📝 房源输入", "📋 总览结论", "🧠 估值分析", "📈 投资测算", "⚠️ 风险分析", "📄 专业报告"]
    active_tab = st.radio("导航", tab_options, horizontal=True, label_visibility="collapsed",
                          key="client_active_tab")

    # 快捷导航按钮
    report_generated = st.session_state.get("report_generated", False)
    if report_generated and active_tab != "📝 房源输入":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("🔙 返回修改房源", use_container_width=True, key="nav_back_input"):
                st.session_state["client_active_tab"] = "📝 房源输入"
                st.rerun()
        with col_nav2:
            if st.button("📄 查看专业报告", use_container_width=True, key="nav_to_report"):
                st.session_state["client_active_tab"] = "📄 专业报告"
                st.rerun()

    if active_tab == "📝 房源输入":
        render_client_input(params)

    elif active_tab == "📋 总览结论":
        if report_generated:
            render_client_overview(params)
        else:
            st.info("👈 请先在「📝 房源输入」页填写信息并点击「📊 生成评估报告」")

    elif active_tab == "🧠 估值分析":
        if report_generated:
            render_client_valuation(params)
        else:
            st.info("👈 请先在「📝 房源输入」页填写信息并点击「📊 生成评估报告」")

    elif active_tab == "📈 投资测算":
        if report_generated:
            render_client_investment(params)
        else:
            st.info("👈 请先在「📝 房源输入」页填写信息并点击「📊 生成评估报告」")

    elif active_tab == "⚠️ 风险分析":
        if report_generated:
            render_client_risk(params)
        else:
            st.info("👈 请先在「📝 房源输入」页填写信息并点击「📊 生成评估报告」")

    elif active_tab == "📄 专业报告":
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
