"""
╔══════════════════════════════════════════════════════════════╗
║  看房AI Book                                               ║
║  北京房产估值与投资决策系统  V6.0                           ║
║  Beijing Property Valuation & Investment Decision System   ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from ui_components import (
    set_global_style,
    render_sidebar_v2,
    render_tab_overview,
    render_tab_valuation,
    render_tab_investment,
    render_tab_risk,
    render_tab_report,
    render_tab_advanced,
    render_poster,
    render_report,
)

# ══════════════════════════════════════════════════════════════
#  页面配置
# ══════════════════════════════════════════════════════════════

set_global_style()

# ══════════════════════════════════════════════════════════════
#  顶部导航栏
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div style="background:linear-gradient(135deg,#1A1A2E,#16213E);padding:16px 24px;
            border-radius:12px;margin-bottom:8px;display:flex;align-items:center;gap:16px">
    <div style="font-size:24px;font-weight:800;color:#FFFFFF;letter-spacing:2px">
        🏠 看房AI Book
    </div>
    <div style="font-size:14px;color:rgba(255,255,255,0.55);margin-left:auto">
        北京房产估值与投资决策系统
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  侧边栏：统一输入
# ══════════════════════════════════════════════════════════════

params = render_sidebar_v2()

# ══════════════════════════════════════════════════════════════
#  顶部操作按钮
# ══════════════════════════════════════════════════════════════

col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
with col_btn1:
    calc_btn = st.button("📊 开始测算", type="primary", use_container_width=True)
with col_btn2:
    poster_btn = st.button("🖼️ 生成海报", use_container_width=True)
with col_btn3:
    report_btn = st.button("📄 完整报告", use_container_width=True)

# ══════════════════════════════════════════════════════════════
#  6 个标签页
# ══════════════════════════════════════════════════════════════

st.divider()

tab_overview, tab_valuation, tab_investment, tab_risk, tab_report, tab_advanced = \
    st.tabs(["📋 总览结论", "🧠 估值分析", "📈 投资测算", "⚠️ 风险分析", "📄 专业报告", "🔧 高级模式"])

# ══════════════════════════════════════════════════════════════
#  Tab A: 总览结论
# ══════════════════════════════════════════════════════════════

with tab_overview:
    if calc_btn:
        render_tab_overview(params)
    else:
        st.info("👈 在侧边栏填写房源信息后，点击「📊 开始测算」查看总览结论")

# ══════════════════════════════════════════════════════════════
#  Tab B: 估值分析
# ══════════════════════════════════════════════════════════════

with tab_valuation:
    if calc_btn:
        render_tab_valuation(params)
    else:
        st.info("👈 点击「📊 开始测算」查看估值分析")

# ══════════════════════════════════════════════════════════════
#  Tab C: 投资测算
# ══════════════════════════════════════════════════════════════

with tab_investment:
    if calc_btn:
        render_tab_investment(params)
    else:
        st.info("👈 点击「📊 开始测算」查看投资测算")

# ══════════════════════════════════════════════════════════════
#  Tab D: 风险分析
# ══════════════════════════════════════════════════════════════

with tab_risk:
    if calc_btn:
        render_tab_risk(params)
    else:
        st.info("👈 点击「📊 开始测算」查看风险分析")

# ══════════════════════════════════════════════════════════════
#  Tab E: 专业报告
# ══════════════════════════════════════════════════════════════

with tab_report:
    render_tab_report(params)

# ══════════════════════════════════════════════════════════════
#  Tab F: 高级模式
# ══════════════════════════════════════════════════════════════

with tab_advanced:
    render_tab_advanced(params)

# ══════════════════════════════════════════════════════════════
#  顶部按钮处理（海报/报告弹窗）
# ══════════════════════════════════════════════════════════════

if poster_btn:
    render_poster()

if report_btn:
    render_report()
