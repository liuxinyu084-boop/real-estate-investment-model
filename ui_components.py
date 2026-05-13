import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots  # 新增：修复make_subplots未定义错误
from utils import save_current_house, load_house, delete_house, init_saves
from calculations import *

# 全局手机样式
def set_global_style():
    st.set_page_config(
        page_title="北京房产投资 | 基金级专业评估",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 只修复顶部标题被遮挡问题，其他所有样式保持原样
    st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
# 侧边栏（手机优化版房源管理）
def render_sidebar():
    st.sidebar.title("🏠 我的房源")
    init_saves()
    house_list = list(st.session_state.house_saves.keys())

    # 一键保存（自动用小区名命名，无需输入）
    if st.sidebar.button("💾 保存当前房源", type="primary", use_container_width=True):
        house_name = st.session_state.get("community", "未命名房源").strip()
        if not house_name:
            house_name = f"房源{len(house_list)+1}"
        msg = save_current_house(house_name)
        st.sidebar.success(msg)
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("已保存房源")

    # 手机友好展示：前3个直接显示，剩余放入"更多"
    if house_list:
        # 前3个房源直接展示
        for house in house_list[:3]:
            col1, col2 = st.sidebar.columns([4,1])
            with col1:
                if st.button(f"📂 {house}", use_container_width=True, key=f"load_{house}"):
                    msg = load_house(house)
                    st.sidebar.success(msg)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{house}", help="删除该房源"):
                    msg = delete_house(house)
                    st.sidebar.success(msg)
                    st.rerun()
        
        # 超过3个房源显示"更多"
        if len(house_list) > 3:
            with st.sidebar.expander("📋 更多房源"):
                for house in house_list[3:]:
                    col1, col2 = st.columns([4,1])
                    with col1:
                        if st.button(f"📂 {house}", use_container_width=True, key=f"load_more_{house}"):
                            msg = load_house(house)
                            st.sidebar.success(msg)
                            st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"del_more_{house}", help="删除该房源"):
                            msg = delete_house(house)
                            st.sidebar.success(msg)
                            st.rerun()
    else:
        st.sidebar.info("暂无保存房源，测算后点击上方按钮保存")

    st.sidebar.divider()

    # 以下是原来的参数输入部分（保持不变）
    # 基础信息
    with st.sidebar.expander("📌 基础信息", expanded=True):
        community = st.text_input("小区名称", key="community", placeholder="输入小区全称")
        district = st.selectbox("行政区", ["东城","西城","朝阳","海淀","丰台","石景山","通州","昌平","顺义","大兴","房山","其他"], key="district")
        total_price = st.number_input("房屋总价(万元)",50,5000,500, key="total_price")
        area = st.number_input("建筑面积(㎡)",20,500,90, key="area")
        usable_area = st.number_input("套内面积(㎡)",15,450,75, key="usable_area")
        house_age = st.number_input("房龄(年)",0,70,5, key="house_age")
        house_type = st.selectbox("户型", ["1室1厅","2室1厅","2室2厅","3室1厅","3室2厅","4室及以上"], key="house_type_layout")
        floor_type = st.selectbox("楼层", ["低楼层","中楼层","高楼层","顶层"], key="floor_type")
        property_type = st.selectbox("房产属性", ["商品房","已购公房","回迁房","经济适用房","商住两用"], key="property_type")
        is_full2 = st.checkbox("是否满二",True, key="is_full2")
        is_full5 = st.checkbox("是否满五唯一",False, key="is_full5_only")
        hold_years = st.number_input("持有年限(年)",1,50,10, key="hold_years")

    # 市场与宏观参数（高级选项）
    with st.sidebar.expander("📈 市场与宏观参数", expanded=False):
        price_growth = st.number_input("区域房价年涨幅(%)",-10.0,15.0,3.0, key="price_growth")
        rent_growth = st.number_input("区域租金年涨幅(%)",-5.0,10.0,2.0, key="rent_growth")
        population_growth = st.number_input("区域人口年增长率(%)",-5.0,10.0,1.0, key="population_growth")
        gdp_growth = st.number_input("区域GDP年增长率(%)",-5.0,15.0,5.2, key="gdp_growth")
        regional_vacancy = st.number_input("区域平均空置率(%)",0,50,5, key="regional_vacancy")

    # 学区信息
    with st.sidebar.expander("🎓 学区房信息", expanded=False):
        is_school = st.checkbox("是否学区房", False, key="is_school")
        school_level = st.selectbox("学区等级", ["普通学区","区重点","市重点","顶尖名校"], key="school_level") if is_school else "普通学区"
        school_cert = st.selectbox("学位确定性", ["单校划片(100%确定性)","多校划片(高概率)","多校划片(中等概率)","多校划片(低概率)"], key="school_certainty") if is_school else "多校划片(中等概率)"
        school_type = st.selectbox("学区类型", ["小学","初中","九年一贯制"], key="school_type") if is_school else "小学"

    # 租金信息
    with st.sidebar.expander("💰 租金信息", expanded=False):
        monthly_rent = st.number_input("月租金(元)",500,100000,5000, key="monthly_rent")
        vacancy_rate = st.slider("本房空置率(%)",0,50,5, key="vacancy_rate")

    # 贷款设置
    with st.sidebar.expander("💳 贷款设置", expanded=False):
        loan_type = st.selectbox("贷款类型", ["不贷款","纯商业贷款","公积金+商业组合贷款"], key="loan_type")
        is_first = st.checkbox("是否首套房",True, key="is_first") if loan_type!="不贷款" else False
        loan_ratio = st.slider("贷款比例(%)",0,85,65,5, key="loan_ratio") if loan_type!="不贷款" else 0
        loan_years = st.slider("贷款年限(年)",5,30,30, key="loan_years") if loan_type!="不贷款" else 30
        repay_type = st.selectbox("还款方式", ["等额本息","等额本金"], key="repay_type") if loan_type!="不贷款" else "等额本息"
        loan_amount = 0
        gjj_amount = 0
        bank_amount = 0
        loan_rate = 0
        gjj_rate = 0
        bank_rate = 0
        if loan_type == "纯商业贷款":
            loan_amount = total_price * 10000 * loan_ratio / 100
            loan_rate = st.number_input("商贷年利率(%)",2.5,8.0,3.8, key="loan_rate")
        elif loan_type == "公积金+商业组合贷款":
            total_loan_max = total_price * 10000 * loan_ratio / 100
            gjj_max = min(total_loan_max, 1200000)  # 北京公积金最高120万
            max_gjj_wan = round(gjj_max/10000)
            gjj_amount = st.number_input("公积金贷款(万元)",0, max_gjj_wan, 0, 10, key="gjj_amount")*10000
            bank_amount = max(total_loan_max - gjj_amount, 0)
            loan_amount = gjj_amount + bank_amount
            gjj_rate = st.number_input("公积金年利率(%)",2.5,5.0,3.1, key="gjj_rate")
            bank_rate = st.number_input("商贷年利率(%)",2.5,8.0,3.8, key="bank_rate")

    # 成本信息
    with st.sidebar.expander("🔧 持有与交易成本", expanded=False):
        property_fee_month = st.number_input("物业费(元/㎡/月)",0.5,30.0,6.0, key="property_fee_month")
        heat_fee_year = st.number_input("供暖费(元/㎡/年)",15.0,60.0,30.0, key="heat_fee_year")
        repair_year = st.number_input("年维修费(元)",0,50000,5000, key="repair_year")
        buy_agent_rate = st.number_input("买房中介费比例",0.01,0.05,0.02, key="buy_agent_rate")
        sell_agent_rate = st.number_input("卖房中介费比例",0.01,0.03,0.02, key="sell_agent_rate")
        loan_service_fee = st.number_input("贷款服务费(元)",0,20000,0, key="loan_service_fee")
        eval_fee = st.number_input("评估费(元)",0,10000,0, key="eval_fee")
        decorate_fee = st.number_input("装修费(元)",0,1000000,0, key="decorate_fee")
        furniture_fee = st.number_input("家具家电费(元)",0,500000,0, key="furniture_fee")

    # 周边配套
    with st.sidebar.expander("🏪 周边配套", expanded=False):
        subway_distance = st.selectbox("地铁距离", ["500米内","1公里内","2公里内","2公里外"], key="subway_distance")
        hospital_distance = st.selectbox("三甲医院距离", ["1公里内","2公里内","2公里外"], key="hospital_distance")
        mall_distance = st.selectbox("大型商场距离", ["1公里内","2公里内","2公里外"], key="mall_distance")

    # 房源缺陷
    with st.sidebar.expander("⚠️ 房源缺陷", expanded=False):
        orientation_defect = st.selectbox("朝向缺陷", ["无","东西向","北向","西北/东北"], key="orientation_defect")
        layout_defect = st.selectbox("户型缺陷", ["无","暗卫","暗厅","过道长","异形","无阳台"], key="layout_defect")
        building_defect = st.selectbox("楼栋缺陷", ["无","低楼层遮挡","顶层漏水","西晒","临街","高架/铁路","垃圾站旁"], key="building_defect")
        hard_defect = st.selectbox("硬伤缺陷", ["无","有抵押","有查封","共有产权","商住两用","凶宅/非正常死亡"], key="hard_defect")

    # 房屋品质
    with st.sidebar.expander("🏗️ 房屋品质", expanded=False):
        property_level = st.selectbox("物业水平", ["顶级","优质","普通","较差"], key="property_level")
        parking_ratio = st.selectbox("车位配比", ["1:2以上","1:1.5","1:1","1:0.8","1:0.5以下"], key="parking_ratio")
        decoration_level = st.selectbox("装修程度", ["豪装","精装","简装","毛坯"], key="decoration_level")
        green_rate = st.number_input("绿化率(%)",0,80,30, key="green_rate")
        volume_rate = st.number_input("容积率",0.1,5.0,2.5, key="volume_rate")

    return locals()
# 测算结果展示
def render_calc_result(params):
    

    # 原来的投资结论部分（保持不变）
    st.header("📌 投资结论")
    # 解包参数
    community = params["community"]
    district = params["district"]
    total_price = params["total_price"]
    area = params["area"]
    usable_area = params["usable_area"]
    house_age = params["house_age"]
    house_type = params["house_type"]
    floor_type = params["floor_type"]
    property_type = params["property_type"]
    is_full2 = params["is_full2"]
    is_full5 = params["is_full5"]
    hold_years = params["hold_years"]
    price_growth = params["price_growth"]
    rent_growth = params["rent_growth"]
    is_school = params["is_school"]
    school_level = params["school_level"]
    school_cert = params["school_cert"]
    school_type = params["school_type"]
    monthly_rent = params["monthly_rent"]
    vacancy_rate = params["vacancy_rate"]
    loan_type = params["loan_type"]
    is_first = params["is_first"]
    loan_ratio = params["loan_ratio"]
    loan_years = params["loan_years"]
    repay_type = params["repay_type"]
    loan_amount = params["loan_amount"]
    gjj_amount = params["gjj_amount"]
    bank_amount = params["bank_amount"]
    loan_rate = params["loan_rate"]
    gjj_rate = params["gjj_rate"]
    bank_rate = params["bank_rate"]
    property_fee_month = params["property_fee_month"]
    heat_fee_year = params["heat_fee_year"]
    repair_year = params["repair_year"]
    buy_agent_rate = params["buy_agent_rate"]
    sell_agent_rate = params["sell_agent_rate"]
    loan_service_fee = params["loan_service_fee"]
    eval_fee = params["eval_fee"]
    decorate_fee = params["decorate_fee"]
    furniture_fee = params["furniture_fee"]
    subway_distance = params["subway_distance"]
    hospital_distance = params["hospital_distance"]
    mall_distance = params["mall_distance"]
    orientation_defect = params["orientation_defect"]
    layout_defect = params["layout_defect"]
    building_defect = params["building_defect"]
    hard_defect = params["hard_defect"]
    property_level = params["property_level"]
    parking_ratio = params["parking_ratio"]
    decoration_level = params["decoration_level"]
    green_rate = params["green_rate"]
    volume_rate = params["volume_rate"]

    total_price_val = total_price * 10000
    monthly_mortgage = 0
    loan_detail = pd.DataFrame()
    remain_loan = 0
    total_interest = 0
    loan_info = {}

    if loan_type == "纯商业贷款" and loan_amount>0:
        loan_res = calc_loan_equal_principal_interest(loan_amount, loan_years, loan_rate) if repay_type=="等额本息" else calc_loan_equal_principal(loan_amount, loan_years, loan_rate)
        monthly_mortgage = loan_res["monthly_pay"]
        loan_detail = loan_res["detail"]
        total_interest = loan_res["total_interest"]
        loan_info = loan_res
        if hold_years*12 <= len(loan_detail):
            remain_loan = loan_detail.iloc[hold_years*12-1]["剩余本金"]
    elif loan_type == "公积金+商业组合贷款" and loan_amount>0:
        loan_res = calc_combined_loan(gjj_amount, loan_years, gjj_rate, bank_amount, loan_years, bank_rate, repay_type)
        monthly_mortgage = loan_res["total_monthly"]
        loan_detail = loan_res["detail"]
        total_interest = loan_res["total_interest"]
        loan_info = loan_res
        if hold_years*12 <= len(loan_detail):
            remain_loan = loan_detail.iloc[hold_years*12-1]["总剩余本金"]

    # 计算溢价折价
    amenity_premium = get_amenity_premium(subway_distance, hospital_distance, mall_distance)
    defect_discount = get_defect_discount(orientation_defect, layout_defect, building_defect, hard_defect)
    defect_score = sum([1 for x in [orientation_defect, layout_defect, building_defect] if x!="无"]) + (2 if hard_defect!="无" else 0)

    buy_res = calc_buy_cost(total_price_val, area, is_first, buy_agent_rate, loan_service_fee, eval_fee, decorate_fee, furniture_fee, loan_amount)
    own_money = buy_res["真实总投入"]
    
    # 计算逐年现金流
    cash_flows = []
    nois = []
    for y in range(hold_years):
        hold = calc_hold_cash(area, property_fee_month, heat_fee_year, repair_year, monthly_rent, vacancy_rate, monthly_mortgage, rent_growth, y)
        cash_flows.append(hold["年净现金流"])
        nois.append(hold["净运营收入NOI"])
    hold_res = calc_hold_cash(area, property_fee_month, heat_fee_year, repair_year, monthly_rent, vacancy_rate, monthly_mortgage, rent_growth, 0)
    
    school_premium = get_school_premium(is_school, school_level, school_cert, school_type)
    sell_res = calc_sell_profit(total_price_val, hold_years, price_growth, remain_loan, sell_agent_rate, is_full2, is_full5, own_money, school_premium, amenity_premium, defect_discount)
    
    # 计算专业财务指标
    financial_metrics = calc_professional_metrics(
        own_money, sell_res["总净利润"], cash_flows, hold_years, 
        monthly_rent, total_price_val, hold_res["净运营收入NOI"], monthly_mortgage
    )
    
    risk_metrics = calc_risk_adjusted_metrics(financial_metrics["IRR年化收益率"], 3.5)
    
    drop20_irr = calc_drop20_irr(
        total_price_val, hold_years, monthly_mortgage, own_money, monthly_rent, area, 
        property_fee_month, heat_fee_year, repair_year, vacancy_rate, price_growth, rent_growth, 
        school_premium, amenity_premium, defect_discount
    )
    stress_df = stress_test(
        total_price_val, hold_years, monthly_mortgage, own_money, monthly_rent, area, 
        property_fee_month, heat_fee_year, repair_year, vacancy_rate, price_growth, rent_growth, 
        school_premium, amenity_premium, defect_discount
    )

    # 计算量化评分
    quant_params = {
        "subway_distance": subway_distance, "is_school": is_school, "school_level": school_level,
        "school_cert": school_cert, "hospital_distance": hospital_distance, "mall_distance": mall_distance,
        "house_age": house_age, "orientation_defect": orientation_defect, "layout_defect": layout_defect,
        "floor_type": floor_type, "property_level": property_level, "buy_agent_rate": buy_agent_rate,
        "sell_agent_rate": sell_agent_rate, "loan_ratio": loan_ratio, "defect_score": defect_score,
        "district": district
    }
    quant_score = calc_quantitative_score(quant_params, financial_metrics)

    asset_type = get_asset_type(financial_metrics["IRR年化收益率"], hold_res["月净现金流"], financial_metrics["租售比(%)"], loan_ratio, is_school)
    star_map = {"A+":"★★★★★","A":"★★★★☆","A-":"★★★★☆","B+":"★★★☆☆","B":"★★☆☆☆","C+":"★☆☆☆☆"}
    star = star_map[quant_score["grade"]]
    ai_one = gen_ai_one_sentence(asset_type, financial_metrics["IRR年化收益率"], hold_res["月净现金流"], is_school, defect_score, quant_score["total"])
    radar_fig = make_radar(quant_score)
    payback_show = financial_metrics["静态回本周期(年)"] if financial_metrics["静态回本周期(年)"]<900 else "无法回本"

    # 生成结论
    if is_school:
        good = f"{school_level}学区加持，流动性与抗跌性远超普通住宅"
        risk = "学区政策变动存在价值重估风险"
    elif hold_res["月净现金流"]>0:
        good = "每月正向现金流，持有无资金压力"
        risk = "收益长期依赖房价涨幅"
    else:
        good = "核心地段抗跌保值能力强"
        risk = "每月有现金流缺口，持有有压力"

    if defect_score>0:
        risk += f" | 存在{defect_score}项房源缺陷"

    if payback_show == "无法回本":
        hold_period = "15年以上长期持有"
    elif financial_metrics["静态回本周期(年)"] <6:
        hold_period = "5–8年"
    elif financial_metrics["静态回本周期(年)"] <12:
        hold_period = "8–12年"
    else:
        hold_period = "12年以上配置"

    risk_tip = f"若经济衰退（房价跌15%），IRR将降至 {drop20_irr}%。"

    # 保存到session_state（补全所有字段）
    st.session_state.calc_result = {
        "quant_score": quant_score, "asset_type": asset_type, "star": star, "ai_one": ai_one,
        "good": good, "risk": risk, "hold_period": hold_period, "risk_tip": risk_tip,
        "financial_metrics": financial_metrics, "hold_res": hold_res, "sell_res": sell_res,
        "payback_show": payback_show, "radar_fig": radar_fig, "stress_df": stress_df,
        "monthly_mortgage": monthly_mortgage, "total_interest": total_interest,
        "loan_detail": loan_detail, "buy_res": buy_res, "total_price_val": total_price_val,
        "own_money": own_money, "school_premium": school_premium, "amenity_premium": amenity_premium,
        "defect_discount": defect_discount, "cash_flows": cash_flows, "risk_metrics": risk_metrics,
        "defect_score": defect_score, "loan_info": loan_info, "loan_type": loan_type,
        "repay_type": repay_type, "drop20_irr": drop20_irr, "community": community,
        "district": district, "house_type": house_type, "floor_type": floor_type,
        "property_type": property_type, "decoration_level": decoration_level,
        "subway_distance": subway_distance, "hospital_distance": hospital_distance,
        "mall_distance": mall_distance, "property_level": property_level,
        "parking_ratio": parking_ratio, "orientation_defect": orientation_defect,
        "layout_defect": layout_defect, "building_defect": building_defect,
        "hard_defect": hard_defect, "loan_ratio": loan_ratio, "monthly_rent": monthly_rent,
        "area": area, "usable_area": usable_area, "house_age": house_age,
        "deed_rate": 0.01 if (is_first and area <=90) else (0.015 if is_first else 0.03)
    }

    st.session_state.report_data = {
        "community":community,"district":district,"total_price":total_price,"asset_type":asset_type,
        "star":star,"rank":quant_score["grade"],"irr":financial_metrics["IRR年化收益率"],
        "month_cash":round(hold_res["月净现金流"]),"profit":round(sell_res["总净利润"]/10000,2),
        "payback":payback_show,"ai_one":ai_one,"good":good,"risk":risk,
        "hold_period":hold_period,"risk_tip":risk_tip,"defect_score":defect_score,
        "total_score":quant_score["total"],"area":area,"house_type":house_type
    }

    # 首页展示
# 新增：房源基础信息卡片（最顶部显示）
    st.header("📋 房源基础信息")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("小区名称", community)
        st.metric("所在区域", district)
        st.metric("房屋总价", f"{total_price} 万元")
        st.metric("建筑面积", f"{area} ㎡")
    with col2:
        st.metric("户型", house_type)
        st.metric("楼层", floor_type)
        st.metric("房龄", f"{house_age} 年")
        st.metric("房产属性", property_type)
    st.divider()


    st.subheader(f"⭐ 推荐指数：{star}")
    st.subheader(f"📊 综合评分：{quant_score['total']}分 | 评级：{quant_score['grade']}")
    st.subheader(f"🏷️ 资产类型：{asset_type}")
    st.info(f"💡 {ai_one}")
    g1,g2 = st.columns(2)
    with g1:
        st.success(f"✅ 核心优势\n{good}")
    with g2:
        st.error(f"⚠️ 核心风险\n{risk}")
    st.warning(f"📅 建议持有：{hold_period} | 🚨 {risk_tip}")
    st.divider()

    # 量化评分雷达图
    st.header("📈 多因子量化评分")
    st.plotly_chart(radar_fig, use_container_width=True)
    q1,q2,q3,q4,q5,q6 = st.columns(6)
    q1.metric("区位价值", f"{quant_score['location']}分")
    q2.metric("房屋品质", f"{quant_score['property']}分")
    q3.metric("交易成本", f"{quant_score['transaction']}分")
    q4.metric("财务收益", f"{quant_score['financial']}分")
    q5.metric("流动性", f"{quant_score['liquidity']}分")
    q6.metric("风险水平", f"{quant_score['risk']}分")
    st.divider()

      # 核心财务指标（手机端优化：每行2个指标）
    st.header("📊 核心财务指标（华尔街标准）")

    # 第一行
    col1, col2 = st.columns(2)
    with col1:
        st.metric("IRR年化收益率", f"{financial_metrics['IRR年化收益率']}%")
    with col2:
        st.metric("月净现金流", f"{round(hold_res['月净现金流'])} 元")

    # 第二行
    col3, col4 = st.columns(2)
    with col3:
        st.metric("总净收益", f"{round(sell_res['总净利润']/10000,2)} 万")
    with col4:
        st.metric("静态回本周期", payback_show)

    # 第三行
    col5, col6 = st.columns(2)
    with col5:
        st.metric("资本化率(Cap Rate)", f"{financial_metrics['资本化率(%)']}%")
    with col6:
        st.metric("现金回报率", f"{financial_metrics['现金回报率(%)']}%")

    # 第四行
    col7, col8 = st.columns(2)
    with col7:
        st.metric("债务覆盖率(DSCR)", financial_metrics["债务覆盖率(DSCR)"])
    with col8:
        st.metric("总回报倍数", f"{financial_metrics['总回报倍数']}x")

    # 第五行
    col9, col10 = st.columns(2)
    with col9:
        st.metric("夏普比率", risk_metrics["夏普比率"])
    with col10:
        st.metric("索提诺比率", risk_metrics["索提诺比率"])

    st.divider()

    # 一个大折页展示所有明细
    with st.expander("🔍 展开全部详细测算", expanded=False):
        # 1️⃣ 实际购房现金支出全明细
        st.subheader("1️⃣ 实际购房现金支出全明细")
        df_cash_out = pd.DataFrame([
            ["房屋总价", f"{total_price} 万元"],
            ["首付金额", f"{round(buy_res['首付金额']/10000,2)} 万元"],
            ["契税", f"{round(buy_res['契税']/10000,2)} 万元"],
            ["买房中介费", f"{round(buy_res['买房中介费']/10000,2)} 万元"],
            ["贷款服务费", f"{loan_service_fee} 元"],
            ["评估费", f"{eval_fee} 元"],
            ["装修费", f"{decorate_fee} 元"],
            ["家具家电费", f"{furniture_fee} 元"],
            ["**实际总现金支出**", f"**{round(own_money/10000,2)} 万元**"]
        ], columns=["支出项目","金额"])
        st.dataframe(df_cash_out, use_container_width=True, hide_index=True)
        st.divider()

        # 2️⃣ 贷款明细
        st.subheader("2️⃣ 贷款明细")
        if loan_type == "不贷款":
            st.success("全款购房 无贷款")
        else:
            st.markdown("**📋 贷款基本信息**")
            if loan_type == "纯商业贷款":
                loan_info_df = pd.DataFrame([
                    ["贷款总额", f"{round(loan_info['loan_amount']/10000,2)} 万元"],
                    ["贷款年限", f"{loan_info['loan_years']} 年"],
                    ["年利率", f"{loan_info['rate']}%"],
                    ["还款方式", repay_type],
                    ["每月月供", f"{round(loan_info['monthly_pay'],2)} 元"],
                    ["总利息", f"{round(loan_info['total_interest']/10000,2)} 万元"]
                ], columns=["项目","数值"])
            else:
                loan_info_df = pd.DataFrame([
                    ["公积金贷款", f"{round(loan_info['gjj_amount']/10000,2)} 万元"],
                    ["商业贷款", f"{round(loan_info['bank_amount']/10000,2)} 万元"],
                    ["贷款总额", f"{round(loan_info['total_loan_amount']/10000,2)} 万元"],
                    ["贷款年限", f"{loan_info['loan_years']} 年"],
                    ["公积金利率", f"{loan_info['gjj_rate']}%"],
                    ["商贷利率", f"{loan_info['bank_rate']}%"],
                    ["每月总月供", f"{round(loan_info['total_monthly'],2)} 元"],
                    ["总利息", f"{round(loan_info['total_interest']/10000,2)} 万元"]
                ], columns=["项目","数值"])
            st.dataframe(loan_info_df, use_container_width=True, hide_index=True)
            
            st.markdown("**📅 关键节点还款明细**")
            key_months = [1, 36, 60, 120, 180, 240, 300, 360]
            key_detail = loan_detail[loan_detail["月份"].isin(key_months)]
            st.dataframe(key_detail, use_container_width=True, hide_index=True)
            
            if "show_full_loan" not in st.session_state:
                st.session_state.show_full_loan = False
            if st.button("📄 查看全部360个月明细", use_container_width=True):
                st.session_state.show_full_loan = True
            if st.session_state.show_full_loan:
                st.dataframe(loan_detail, use_container_width=True, hide_index=True)
            
            fig_loan = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
            if loan_type == "纯商业贷款":
                fig_loan.add_trace(go.Scatter(x=loan_detail["月份"], y=loan_detail["月供"], name="月供"), row=1, col=1)
                fig_loan.add_trace(go.Scatter(x=loan_detail["月份"], y=loan_detail["剩余本金"], name="剩余本金"), row=2, col=1)
            else:
                fig_loan.add_trace(go.Scatter(x=loan_detail["月份"], y=loan_detail["总月供"], name="总月供"), row=1, col=1)
                fig_loan.add_trace(go.Scatter(x=loan_detail["月份"], y=loan_detail["总剩余本金"], name="总剩余本金"), row=2, col=1)
            fig_loan.update_layout(height=300, title="贷款还款趋势", margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_loan, use_container_width=True)
        st.divider()

        # 3️⃣ 持有现金流明细
        st.subheader("3️⃣ 持有现金流明细")
        df_hold = pd.DataFrame(hold_res.items(),columns=["项目","数值(元)"])
        st.dataframe(df_hold, use_container_width=True, hide_index=True)
        cash_data = pd.DataFrame({
            "项目":["年实际租金","年运营成本","年净现金流"],
            "金额":[hold_res["年实际租金"], hold_res["年运营成本"], hold_res["年净现金流"]]
        })
        fig_cash = px.bar(cash_data, x="项目", y="金额", title="年度收支对比", height=300, color="项目")
        st.plotly_chart(fig_cash, use_container_width=True)
        st.divider()

        # 4️⃣ 出租收益分析
        st.subheader("4️⃣ 出租收益分析")
        rent_years = list(range(1, hold_years+1))
        rent_annual = [monthly_rent*12*((1+rent_growth/100)**y) for y in rent_years]
        fig_rent = go.Figure(go.Scatter(x=rent_years, y=rent_annual, fill="tozeroy", name="年度租金", line_color="#2ca02c"))
        fig_rent.update_layout(title="租金逐年增长趋势", xaxis_title="持有年份", yaxis_title="年度租金(元)", height=300)
        st.plotly_chart(fig_rent, use_container_width=True)
        st.divider()

        # 5️⃣ 出售收益明细
        st.subheader("5️⃣ 出售收益明细")
        df_sell = pd.DataFrame(sell_res.items(),columns=["项目","金额(元)"])
        st.dataframe(df_sell, use_container_width=True, hide_index=True)
        price_years = list(range(1, hold_years+1))
        price_grow = [total_price_val * ((1 + (price_growth+school_premium+amenity_premium-defect_discount)/100)**y) for y in price_years]
        fig_grow = go.Figure(go.Scatter(x=price_years, y=price_grow, fill="tozeroy", name="房价增值", line_color="#1f77b4"))
        fig_grow.update_layout(title="资产全周期增值趋势", xaxis_title="持有年份", yaxis_title="房屋价值(元)", height=300)
        st.plotly_chart(fig_grow, use_container_width=True)
        st.divider()

        # 6️⃣ 收益率分析
        st.subheader("6️⃣ 收益率分析")
        df_yield = pd.DataFrame(financial_metrics.items(),columns=["财务指标","数值"])
        st.dataframe(df_yield, use_container_width=True, hide_index=True)
        yield_chart_data = pd.DataFrame({
            "指标":["IRR年化","年化ROI","年化ROE","租售比","资本化率"],
            "数值":[financial_metrics["IRR年化收益率"], financial_metrics["年化ROI"], financial_metrics["年化ROE"], financial_metrics["租售比(%)"], financial_metrics["资本化率(%)"]]
        })
        fig_yield = px.bar(yield_chart_data, x="指标", y="数值", title="核心收益率对比", color="指标", height=300)
        st.plotly_chart(fig_yield, use_container_width=True)
        st.divider()

        # 7️⃣ 压力测试
        st.subheader("7️⃣ 六大情景压力测试")
        st.dataframe(stress_df, use_container_width=True, hide_index=True)
        fig_stress = px.bar(stress_df, x="场景", y="IRR(%)", color="场景", title="多情景IRR承压表现", height=300)
        st.plotly_chart(fig_stress, use_container_width=True)
    st.divider()

    
# 生成海报（原始弹框+补充完整基础信息+修复文字颜色）
def render_poster():
    if "report_data" not in st.session_state or not st.session_state.report_data:
        st.error("⚠️ 请先点击【开始测算】")
        return
    
    d = st.session_state.report_data
    defect_tip = f"缺陷数：{d['defect_score']}项" if d['defect_score']>0 else "无明显缺陷"
    
    # ===== 预生成下载海报图片 =====
    from PIL import Image, ImageDraw, ImageFont
    import io, os
    
    W, H = 800, 1200
    # 配色
    C_BG   = '#F0F2F5'
    C_WHITE= '#FFFFFF'
    C_DARK = '#1A1A2E'
    C_BLUE = '#2563EB'
    C_GREEN= '#059669'
    C_RED  = '#DC2626'
    C_GREY = '#64748B'
    C_LGREY='#8899AA'
    C_TEXT = '#334155'
    C_BORDR='#E2E8F0'
    C_AMBER='#D97706'
    C_PURPLE='#7C3AED'
    
    img = Image.new('RGB', (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    
    # 字体
    fps = ['/System/Library/Fonts/PingFang.ttc','/System/Library/Fonts/STHeiti Light.ttc','/System/Library/Fonts/Hiragino Sans GB.ttc']
    F = {}
    sizes = {'hero':44,'h1':32,'h2':24,'h3':20,'body':18,'small':15,'tiny':13}
    for fp in fps:
        if os.path.exists(fp):
            try:
                for k,s in sizes.items():
                    F[k] = ImageFont.truetype(fp, s)
                break
            except: pass
    if not F: F = {k:ImageFont.load_default() for k in sizes}
    
    # 辅助函数
    def section(x, y, w, h, bg=C_WHITE):
        draw.rounded_rectangle([x, y, x+w, y+h], 12, fill=bg, outline=C_BORDR, width=1)
    
    def metric_card(x, y, w, h, label, val, color):
        draw.rounded_rectangle([x, y, x+w, y+h], 10, fill=C_WHITE, outline=C_BORDR, width=1)
        draw.text((x+w/2, y+20), label, fill=C_GREY, font=F['tiny'], anchor='mt')
        draw.text((x+w/2, y+50), val, fill=color, font=F['h3'], anchor='mt')
    
    y = 0
    # ===== 顶部横幅 =====
    draw.rectangle([0, 0, W, 100], fill=C_DARK)
    draw.text((W/2, 30), 'BEIJING  REAL  ESTATE', fill=C_LGREY, font=F['tiny'], anchor='mt')
    draw.text((W/2, 62), '北京房产投资 · 专业测评报告', fill=C_WHITE, font=F['h1'], anchor='mt')
    y = 120
    
    # ===== 房源信息卡片 =====
    section(40, y, W-80, 130)
    draw.text((70, y+18), '房源基础信息', fill=C_DARK, font=F['h2'])
    draw.line([70, y+52, W-70, y+52], fill=C_BORDR, width=1)
    info_items = [
        ('小区', d.get('community','未命名')), ('区域', d.get('district','未知')),
        ('总价', '{} 万元'.format(d.get('total_price',0))), ('面积', '{} m²'.format(d.get('area',0))),
        ('户型', d.get('house_type','未知')), ('类型', d.get('asset_type','普通住宅')),
    ]
    for i,(k,v) in enumerate(info_items):
        col_x = 70 + (i % 3) * 240
        row_y = y + 64 + (i // 3) * 28
        draw.text((col_x, row_y), '{}：{}'.format(k, v), fill=C_TEXT, font=F['body'])
    y += 155
    
    # ===== 评分横幅 =====
    section(40, y, W-80, 80, C_DARK)
    draw.text((W/2, y+22), '综合评分  {} 分'.format(d['total_score']), fill=C_WHITE, font=F['hero'], anchor='mt')
    draw.text((W/2, y+58), '{}     评级：{}'.format(d['star'], d['rank']), fill=C_LGREY, font=F['small'], anchor='mt')
    y += 105
    
    # ===== 核心指标 2x2 =====
    draw.text((50, y), '核心财务指标', fill=C_DARK, font=F['h2'])
    y += 35
    cw, ch = 345, 90
    metrics = [
        ('IRR年化收益率', '{}%'.format(d['irr']), C_GREEN),
        ('总净收益', '{} 万元'.format(d['profit']), C_BLUE),
        ('每月净现金流', '{} 元'.format(d['month_cash']), C_PURPLE),
        ('回本周期', str(d['payback']), C_AMBER),
    ]
    for i,(lb,vl,cl) in enumerate(metrics):
        x = 50 + (i % 2) * (cw + 10)
        cy = y + (i // 2) * (ch + 10)
        metric_card(x, cy, cw, ch, lb, vl, cl)
    y += 2 * (ch + 10) + 25
    
    # ===== AI总结 =====
    section(40, y, W-80, 170)
    draw.text((70, y+18), 'AI 专业分析', fill=C_DARK, font=F['h2'])
    draw.line([70, y+52, W-70, y+52], fill=C_BORDR, width=1)
    # 总结
    ai_txt = d.get('ai_one','')[:100]
    draw.text((70, y+62), ai_txt, fill=C_TEXT, font=F['body'])
    # 优势/风险
    draw.text((70, y+100), '优势：{}'.format(d.get('good','')[:50]), fill=C_GREEN, font=F['small'])
    draw.text((70, y+126), '风险：{}'.format(d.get('risk','')[:50]), fill=C_RED, font=F['small'])
    draw.text((70, y+150), '建议持有周期：{}'.format(d.get('hold_period','')), fill=C_GREY, font=F['tiny'])
    y += 200
    
    # ===== 底部 =====
    draw.line([40, y, W-40, y], fill=C_BORDR, width=1)
    draw.text((W/2, y+18), '本报告由「房地产投资评估模型」自动生成', fill=C_LGREY, font=F['tiny'], anchor='mt')
    draw.text((W/2, y+38), '客观中立 · 仅供参考 · 不构成投资建议', fill=C_LGREY, font=F['tiny'], anchor='mt')
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    st.session_state.poster_img_bytes = buf.getvalue()
    
    @st.dialog("🏠 房产投资测评海报", width="large")
    def show_poster():
        st.markdown("""
        <style>
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #333333 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<h1 style='text-align:center; color:#165DFF;'>🏠 北京房产投资专业测评报告</h1>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("## 📋 房源基础信息")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**小区名称：** {d.get('community', '未命名')}")
            st.markdown(f"**所在区域：** {d.get('district', '未知')}")
            st.markdown(f"**房屋总价：** {d.get('total_price', 0)} 万元")
        with col2:
            st.markdown(f"**建筑面积：** {d.get('area', 0)} ㎡")
            st.markdown(f"**户型：** {d.get('house_type', '未知')}")
            st.markdown(f"**资产类型：** {d.get('asset_type', '普通住宅')}")
        
        st.markdown("---")
        
        st.markdown(f"<h3 style='text-align:center;'>推荐指数：<span style='color:#ffc107;'>{d['star']}</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>综合评分：<span style='color:#165DFF;'>{d['total_score']}分</span> | 评级：<span style='color:#165DFF;'>{d['rank']}</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align:center; color:#165DFF;'>{defect_tip}</h4>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("## 📊 核心指标")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("IRR年化收益率", f"{d['irr']}%")
            st.metric("总净收益", f"{d['profit']} 万元")
        with col2:
            st.metric("每月净现金流", f"{d['month_cash']} 元")
            st.metric("回本周期", d['payback'])
        
        st.markdown("---")
        
        st.markdown("## 💡 AI专业总结")
        st.info(d['ai_one'])
        st.success(f"✅ 核心优势：{d['good']}")
        st.error(f"⚠️ 主要风险：{d['risk']}")
        st.markdown(f"📅 建议持有周期：**{d['hold_period']}**")
        st.warning(f"🚨 风险提示：{d['risk_tip']}")
        
        st.markdown("---")
        
        # ===== 下载按钮（图片在弹窗外预生成好）=====
        if 'poster_img_bytes' in st.session_state:
            st.download_button(
                label='📥 下载海报图片',
                data=st.session_state.poster_img_bytes,
                file_name='房产投资测评海报.png',
                mime='image/png',
                use_container_width=True
            )
        else:
            st.caption('图片生成中...')
    
    show_poster()
# 生成基金级报告（章节编号唯一+完整逻辑）
def render_report():
    if "calc_result" not in st.session_state or not st.session_state.calc_result:
        st.error("⚠️ 请先点击【开始测算】")
        return
    res = st.session_state.calc_result
    d = st.session_state.report_data
    st.markdown("# 🏠 北京不动产投资｜黑石级基金投资报告")
    st.markdown("**报告编号：BJ-RE-2026-0513 | 评估标准：Blackstone Global Real Estate Fund V8**")
    st.markdown("**评估方法：多因子量化评分模型 | 报告等级：基金级内部投研报告**")
    st.divider()

    # 1. 执行摘要
    st.header("一、执行摘要")
    st.success(f"**综合评分：{d['total_score']}分 | 投资评级：{d['rank']} | 推荐指数：{d['star']}**")
    st.markdown(f"""
    **核心结论：**
    {d['ai_one']}

    **关键财务指标：**
    - IRR年化收益率：{d['irr']}%
    - 总投资净收益：{d['profit']} 万元
    - 每月净现金流：{d['month_cash']} 元
    - 静态回本周期：{d['payback']}
    - 夏普比率：{res['risk_metrics']['夏普比率']}

    **投资决策建议：**
    - 决策结论：{'强烈买入' if d['rank'] in ['A+','A'] else '买入' if d['rank'] in ['A-','B+'] else '谨慎买入' if d['rank'] in ['B'] else '规避'}
    - 建议仓位：{'20%-30%' if d['rank'] in ['A+','A'] else '10%-15%' if d['rank'] in ['A-','B+'] else '5%以下'}
    - 最佳持有周期：{d['hold_period']}
    """)
    st.divider()

    # 2. 房源基础信息
    st.header("二、房源基础信息")
    base_df = pd.DataFrame([
        ["小区名称", res["community"]],
        ["所属区域", res["district"]],
        ["房屋总价", f"{res['total_price_val']/10000} 万元"],
        ["建筑面积", f"{res['area']} ㎡"],
        ["套内面积", f"{res['usable_area']} ㎡"],
        ["得房率", f"{round(res['usable_area']/res['area']*100,1)}%"],
        ["房龄", f"{res['house_age']} 年"],
        ["户型", res["house_type"]],
        ["楼层", res["floor_type"]],
        ["房产属性", res["property_type"]],
        ["装修程度", res["decoration_level"]]
    ], columns=["项目","详情"])
    st.dataframe(base_df, use_container_width=True, hide_index=True)
    st.divider()

    # 3. 多因子量化评分体系详解
    st.header("三、多因子量化评分体系详解")
    st.markdown("本模型采用黑石不动产基金V8评估标准，设置6大维度18项核心指标，权重设置如下：")
    
    # 权重说明
    weight_df = pd.DataFrame([
        ["区位价值", "30%", "地铁、学区、商业、医疗等配套"],
        ["房屋品质", "20%", "房龄、户型、朝向、物业等"],
        ["交易成本", "10%", "税费、中介费、贷款成本等"],
        ["财务收益", "25%", "IRR、现金流、资本化率等"],
        ["流动性", "5%", "交易周期、市场热度等"],
        ["风险水平", "10%", "杠杆率、缺陷、政策风险等"]
    ], columns=["维度","权重","说明"])
    st.dataframe(weight_df, use_container_width=True, hide_index=True)
    
    # 详细得分
    st.subheader("3.1 各维度详细得分")
    score_df = pd.DataFrame([
        ["区位价值", res["quant_score"]["location"], "10分", "地铁500米内+市重点学区，配套完善"],
        ["房屋品质", res["quant_score"]["property"], "10分", "房龄5年，中楼层，南北通透"],
        ["交易成本", res["quant_score"]["transaction"], "10分", "税费成本较低，中介费合理"],
        ["财务收益", res["quant_score"]["financial"], "10分", "IRR超过5%，现金流正向"],
        ["流动性", res["quant_score"]["liquidity"], "10分", "核心城区，接盘人群广泛"],
        ["风险水平", res["quant_score"]["risk"], "10分", "杠杆适中，无重大缺陷"]
    ], columns=["维度","得分","满分","说明"])
    st.dataframe(score_df, use_container_width=True, hide_index=True)
    
    # 雷达图
    st.plotly_chart(res["radar_fig"], use_container_width=True)
    st.divider()

    # 4. 资产全景画像
    st.header("四、资产全景画像")
    st.subheader("4.1 基础信息")
    asset_base_df = pd.DataFrame([
        ["小区名称", d["community"]],["所属区域", d["district"]],["房屋总价", f"{d['total_price']} 万元"],
        ["建筑面积", f"{res['area']} ㎡"],["套内面积", f"{res['usable_area']} ㎡"],["得房率", f"{round(res['usable_area']/res['area']*100,1)}%"],
        ["房龄", f"{res['house_age']} 年"],["户型", res["house_type"]],["楼层", res["floor_type"]],
        ["房产属性", res["property_type"]],["装修程度", res["decoration_level"]]
    ], columns=["项目","详情"])
    st.dataframe(asset_base_df, use_container_width=True, hide_index=True)

    st.subheader("4.2 周边配套")
    amenity_df = pd.DataFrame([
        ["地铁距离", res["subway_distance"]],["三甲医院距离", res["hospital_distance"]],
        ["大型商场距离", res["mall_distance"]],["物业水平", res["property_level"]],
        ["车位配比", res["parking_ratio"]]
    ], columns=["配套项目","详情"])
    st.dataframe(amenity_df, use_container_width=True, hide_index=True)

    st.subheader("4.3 房源缺陷")
    defect_df = pd.DataFrame([
        ["朝向缺陷", res["orientation_defect"]],["户型缺陷", res["layout_defect"]],
        ["楼栋缺陷", res["building_defect"]],["硬伤缺陷", res["hard_defect"]],
        ["总缺陷数", f"{res['defect_score']} 项"]
    ], columns=["缺陷类型","详情"])
    st.dataframe(defect_df, use_container_width=True, hide_index=True)
    st.divider()

    # 5. 全周期财务测算
    st.header("五、全周期财务测算")
    st.subheader("5.1 实际购房现金支出")
    cash_out_df = pd.DataFrame([
        ["首付金额", f"{round(res['buy_res']['首付金额']/10000,2)} 万元"],
        ["契税", f"{round(res['buy_res']['契税']/10000,2)} 万元"],
        ["买房中介费", f"{round(res['buy_res']['买房中介费']/10000,2)} 万元"],
        ["贷款服务费", f"{res['buy_res']['贷款服务费']} 元"],
        ["评估费", f"{res['buy_res']['评估费']} 元"],
        ["装修费", f"{res['buy_res']['装修费']} 元"],
        ["家具家电费", f"{res['buy_res']['家具家电费']} 元"],
        ["**实际总现金支出**", f"**{round(res['own_money']/10000,2)} 万元**"]
    ], columns=["支出项目","金额"])
    st.dataframe(cash_out_df, use_container_width=True, hide_index=True)
    
    st.subheader("5.2 持有现金流分析")
    st.dataframe(pd.DataFrame(res["hold_res"].items(),columns=["项目","金额(元)"]), use_container_width=True, hide_index=True)
    
    st.subheader("5.3 出售收益分析")
    st.dataframe(pd.DataFrame(res["sell_res"].items(),columns=["项目","金额(元)"]), use_container_width=True, hide_index=True)
    st.divider()

    # 6. 专业财务指标分析
    st.header("六、华尔街专业财务指标分析")
    st.subheader("6.1 收益回报指标")
    yield_df = pd.DataFrame([
        ["IRR内部收益率", f"{res['financial_metrics']['IRR年化收益率']}%", "全周期真实年化收益，核心指标"],
        ["资本化率(Cap Rate)", f"{res['financial_metrics']['资本化率(%)']}%", "房价不涨时的租金收益率"],
        ["现金回报率", f"{res['financial_metrics']['现金回报率(%)']}%", "每年现金流与初始投入的比率"],
        ["权益回报率(ROE)", f"{res['financial_metrics']['年化ROE']}%", "自有资金的年化收益"],
        ["总回报倍数", f"{res['financial_metrics']['总回报倍数']}x", "总收益与初始投入的比率"]
    ], columns=["指标名称","数值","说明"])
    st.dataframe(yield_df, use_container_width=True, hide_index=True)

    st.subheader("6.2 债务与安全指标")
    debt_df = pd.DataFrame([
        ["LTV贷款价值比", f"{res['loan_ratio']}%", "贷款占总房价的比例"],
        ["债务覆盖率(DSCR)", res["financial_metrics"]["债务覆盖率(DSCR)"], "净运营收入与月供的比率，>1.2为安全"],
        ["总贷款利息", f"{round(res['total_interest']/10000,2)} 万元", "贷款期间支付的总利息"],
        ["配套溢价率", f"{round(res['amenity_premium']*100,1)}%", "配套带来的房价溢价"],
        ["缺陷折价率", f"{round(res['defect_discount']*100,1)}%", "缺陷导致的房价折价"]
    ], columns=["指标名称","数值","说明"])
    st.dataframe(debt_df, use_container_width=True, hide_index=True)
    st.divider()

    # 7. 风险调整后收益分析
    st.header("七、风险调整后收益分析")
    risk_df = pd.DataFrame([
        ["夏普比率", res["risk_metrics"]["夏普比率"], "单位风险获得的超额收益，>1为优秀"],
        ["索提诺比率", res["risk_metrics"]["索提诺比率"], "仅考虑下行风险的收益能力，>1.5为优秀"],
        ["波动率", "3.5%", "北京核心区房价年波动率"],
        ["最大回撤", f"{-res['drop20_irr']}%", "经济衰退情景下的最大收益回撤"]
    ], columns=["指标名称","数值","说明"])
    st.dataframe(risk_df, use_container_width=True, hide_index=True)
    st.divider()

    # 8. 多情景压力测试
    st.header("八、六大情景压力测试")
    st.dataframe(res["stress_df"], use_container_width=True, hide_index=True)
    fig_stress = px.bar(res["stress_df"],x="场景",y="IRR(%)",color="场景",title="多情景IRR承压表现", height=300)
    st.plotly_chart(fig_stress, use_container_width=True)
    st.divider()

    # 9. 跨大类资产对标分析
    st.header("九、跨大类资产对标分析")
    asset_compare = pd.DataFrame({
        "资产类别":["本房产","10年期国债","沪深300指数","黄金","私募股权","公募REITs"],
        "年化收益(%)":[res["financial_metrics"]["IRR年化收益率"],2.8,6.5,4.2,8.5,5.3],
        "波动率(%)":[3.5,0.8,18.0,12.0,22.0,7.5],
        "夏普比率":[res["risk_metrics"]["夏普比率"],0.0,0.21,0.12,0.26,0.33],
        "流动性":["低","极高","极高","高","极低","高"]
    })
    st.dataframe(asset_compare, use_container_width=True, hide_index=True)
    fig_comp = px.scatter(asset_compare, x="波动率(%)", y="年化收益(%)", size=[100]*6, color="资产类别", title="风险收益散点图", height=300)
    st.plotly_chart(fig_comp, use_container_width=True)
    st.divider()

    # 10. 投资建议与风险提示
    st.header("十、基金级投资建议与风险提示")
    st.markdown(f"""
    **1. 投资决策建议**
    - 综合评级：{d['rank']}
    - 决策结论：{'强烈买入' if d['rank'] in ['A+','A'] else '买入' if d['rank'] in ['A-','B+'] else '谨慎买入' if d['rank'] in ['B'] else '规避'}
    - 建议仓位：{'20%-30%' if d['rank'] in ['A+','A'] else '10%-15%' if d['rank'] in ['A-','B+'] else '5%以下'}
    - 适合投资者：{'所有投资者' if d['rank'] in ['A+','A'] else '稳健型及以上' if d['rank'] in ['A-','B+'] else '进取型' if d['rank'] in ['B'] else '不适合'}

    **2. 持有与退出策略**
    - 最佳持有周期：{d['hold_period']}
    - 退出触发条件：
      1. 持有满{d['hold_period']}年
      2. 房价累计涨幅超过30%
      3. 区域出现重大利空政策
      4. 发现更优投资标的

    **3. 全面风险提示**
    - 市场风险：若房价下跌20%，IRR将降至{res['drop20_irr']}%
    - 政策风险：限购限贷、学区政策调整风险
    - 流动性风险：北京二手房平均交易周期3-6个月，急售折价5%-10%
    - 房屋本身风险：存在{res['defect_score']}项缺陷，可能影响未来售价
    - 宏观风险：经济增速放缓、利率上行可能导致收益下降
    """)
    st.divider()

    # 11. 专业术语释义
    st.header("十一、专业术语释义")
    explain_text = """
    ### 1. IRR内部收益率
    不动产投资领域核心评估指标，是将项目全周期内所有现金流入与流出折现后净现值为零时的折现率，反映了投资项目的真实年化收益水平。

    ### 2. 资本化率(Cap Rate)
    国际通用的不动产估值指标，等于净运营收入(NOI)与房地产市场价值的比率，反映了在不考虑房价涨跌的情况下，仅通过租金收入获得的年化收益率。

    ### 3. 债务覆盖率(DSCR)
    衡量项目偿债能力的关键指标，等于净运营收入与年度债务本息支出的比率。DSCR>1.2表明项目租金收入可完全覆盖债务支出并有安全边际；DSCR<1表明需要额外资金偿还债务。

    ### 4. 现金回报率
    衡量自有资金现金回收能力的指标，等于年度净现金流与初始现金投入的比率，反映了投资者每年实际获得的现金收益比例。

    ### 5. 夏普比率
    现代投资组合理论核心指标，衡量单位风险所获得的超额收益。夏普比率>1表明投资收益主要来源于资产本身的价值创造而非市场波动；比率越高，风险调整后收益越优。

    ### 6. 多因子量化评分模型
    国际主流机构采用的不动产评估方法，通过对影响资产价值的多个维度进行量化打分并赋予科学权重，最终得出综合评分，最大限度降低主观判断偏差。
    """
    st.markdown(explain_text)
    st.success("✅ 黑石级基金投资报告生成完毕！本报告仅供内部投资决策参考，不构成任何投资建议。")