import streamlit as st
from ui_components import set_global_style, render_sidebar, render_calc_result, render_poster, render_report, render_valuation

# 设置全局样式（仅修复标题遮挡）
set_global_style()

# 页面标题
st.title("🏠 北京房产投资 | 基金级专业评估")
st.divider()

# 渲染侧边栏获取参数
params = render_sidebar()

# ====================== 顶部固定按钮区域（永远在最上方）======================
col1, col2 = st.columns(2)
with col1:
    calc_btn = st.button("📊 开始测算", type="primary", use_container_width=True)

with col2:
    poster_btn_top = st.button("🖼️ 生成海报", use_container_width=True)

report_btn_top = st.button("📄 生成基金级投资报告", use_container_width=True)

val_btn_top = st.button("🧠 AI估值分析", use_container_width=True)
st.divider()

# ====================== 结果显示区域 ======================
result_container = st.container()

with result_container:
    if calc_btn:
        # 执行计算并显示结果
        render_calc_result(params)
        
        # 结果顶部快捷按钮（测算后自动显示，无需滚动回顶部）
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖼️ 生成海报（快捷）", use_container_width=True):
                render_poster()
        with col2:
            if st.button("📄 生成基金级报告（快捷）", use_container_width=True):
                render_report()

# 处理顶部按钮点击
if poster_btn_top:
    render_poster()

if report_btn_top:
    render_report()

if val_btn_top:
    render_valuation(params)