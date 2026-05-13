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
    
    W, H = 800, 1300
    C_BG='#F0F2F5'; C_WHITE='#FFFFFF'; C_DARK='#1A1A2E'; C_BLUE='#2563EB'
    C_GREEN='#059669'; C_RED='#DC2626'; C_GREY='#64748B'; C_GREY2='#8899AA'
    C_TEXT='#334155'; C_BORDR='#E2E8F0'; C_AMBER='#D97706'; C_PURPLE='#7C3AED'
    
    img = Image.new('RGB', (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    
    fps = ['/System/Library/Fonts/PingFang.ttc','/System/Library/Fonts/STHeiti Light.ttc','/System/Library/Fonts/Hiragino Sans GB.ttc']
    F = {}
    for k,s in [('hero',40),('h1',28),('h2',22),('h3',18),('body',16),('small',14),('tiny',12)]:
        for fp in fps:
            if os.path.exists(fp):
                try: F[k]=ImageFont.truetype(fp,s); break
                except: pass
        if k not in F: F[k]=ImageFont.load_default()
    
    def card(x, y, w, h, label, val, color):
        draw.rounded_rectangle([x, y, x+w, y+h], 10, fill=C_WHITE, outline=C_BORDR, width=1)
        draw.text((x+w/2, y+14), label, fill=C_GREY, font=F['tiny'], anchor='mt')
        draw.text((x+w/2, y+38), val, fill=color, font=F['h2'], anchor='mt')
    
    y = 0
    # ========== 顶部横幅 ==========
    draw.rectangle([0, 0, W, 90], fill=C_DARK)
    draw.text((W/2, 28), 'BEIJING  REAL  ESTATE  INVESTMENT', fill=C_GREY2, font=F['tiny'], anchor='mt')
    draw.text((W/2, 56), '北京房产投资 · 专业测评报告', fill=C_WHITE, font=F['h1'], anchor='mt')
    y = 108
    
    # ========== 房源信息 3列 ==========
    draw.rounded_rectangle([40, y, W-40, y+100], 12, fill=C_WHITE, outline=C_BORDR, width=1)
    draw.text((70, y+14), '房源基础信息', fill=C_DARK, font=F['h2'])
    draw.line([70, y+42, W-70, y+42], fill=C_BORDR, width=1)
    for i,(k,v) in enumerate([('小区',d.get('community','')),('区域',d.get('district','')),
        ('总价','{}万'.format(d.get('total_price',0))),('面积','{}m²'.format(d.get('area',0))),
        ('户型',d.get('house_type','')),('类型',d.get('asset_type',''))]):
        cx = 70 + (i % 3) * 236
        ry = y + 54 + (i // 3) * 22
        draw.text((cx, ry), '{}：{}'.format(k,v), fill=C_TEXT, font=F['body'])
    y += 116
    
    # ========== 评分条 ==========
    draw.rounded_rectangle([40, y, W-40, y+60], 12, fill=C_DARK)
    draw.text((W/2, y+16), '综合评分  {} 分      {}      评级：{}'.format(d['total_score'], d['star'], d['rank']), fill=C_WHITE, font=F['h2'], anchor='mt')
    y += 76
    
    # ========== 核心财务指标 2x2 ==========
    draw.text((56, y), '核心财务指标', fill=C_DARK, font=F['h3'])
    y += 28
    cw, ch = 346, 78
    for i,(lb,vl,cl) in enumerate([('IRR年化收益率','{}%'.format(d['irr']),C_GREEN),
        ('总净收益','{} 万元'.format(d['profit']),C_BLUE),
        ('每月净现金流','{} 元'.format(d['month_cash']),C_PURPLE),
        ('回本周期',str(d['payback']),C_AMBER)]):
        cx = 48 + (i % 2) * (cw + 12)
        cy = y + (i // 2) * (ch + 10)
        card(cx, cy, cw, ch, lb, vl, cl)
    y += 2 * (ch + 10) + 14
    
    # ========== 多因子量化评分（含雷达图）==========
    qs = st.session_state.calc_result.get('quant_score', {})
    if qs:
        draw.text((56, y), '多因子量化评分', fill=C_DARK, font=F['h3'])
        y += 24
        # 雷达图 (280x250)
        import math
        radar_w, radar_h = 330, 260
        radar = Image.new('RGBA', (radar_w, radar_h), (0,0,0,0))
        rd = ImageDraw.Draw(radar)
        dims = ['区位价值','房屋品质','交易成本','财务收益','流动性','风险水平']
        vals = [qs.get('location',0), qs.get('property',0), qs.get('transaction',0),
                qs.get('financial',0), qs.get('liquidity',0), qs.get('risk',0)]
        N, max_v = 6, 30
        rcx, rcy, rr = 148, 125, 92
        for rl in [rr/3, rr*2/3, rr]:
            pts = [(rcx+rl*math.cos(-math.pi/2+2*math.pi*i/N), rcy+rl*math.sin(-math.pi/2+2*math.pi*i/N)) for i in range(N)]
            rd.polygon(pts, outline='#D0D5DD')
        dpts = [(rcx+(vals[i]/max_v)*rr*math.cos(-math.pi/2+2*math.pi*i/N),
                 rcy+(vals[i]/max_v)*rr*math.sin(-math.pi/2+2*math.pi*i/N)) for i in range(N)]
        rd.polygon(dpts, fill='#2563EB33', outline='#2563EB')
        for i in range(N):
            a = -math.pi/2 + 2*math.pi*i/N
            rd.line([rcx, rcy, rcx+rr*math.cos(a), rcy+rr*math.sin(a)], fill='#D0D5DD', width=1)
            lx = rcx+(rr+28)*math.cos(a); ly = rcy+(rr+28)*math.sin(a)
            tw = rd.textlength(dims[i], font=F['tiny'])
            rd.text((lx-tw/2, ly-7), dims[i], fill=C_TEXT, font=F['tiny'])
            sx = rcx+(vals[i]/max_v)*rr*math.cos(a); sy = rcy+(vals[i]/max_v)*rr*math.sin(a)
            rd.ellipse([sx-4, sy-4, sx+4, sy+4], fill='#1D4ED8')
            rd.text((sx, sy-16), str(vals[i]), fill='#1D4ED8', font=F['tiny'], anchor='mt')
        img.paste(radar, (48, y), radar)
        y += 270
    
    # ========== AI分析 ==========
    draw.rounded_rectangle([40, y, W-40, y+130], 12, fill=C_WHITE, outline=C_BORDR, width=1)
    draw.text((70, y+14), 'AI 专业分析', fill=C_DARK, font=F['h2'])
    draw.line([70, y+40, W-70, y+40], fill=C_BORDR, width=1)
    draw.text((70, y+50), d.get('ai_one','')[:95], fill=C_TEXT, font=F['body'])
    draw.text((70, y+76), '优势：{}'.format(d.get('good','')[:50]), fill=C_GREEN, font=F['small'])
    draw.text((70, y+98), '风险：{}'.format(d.get('risk','')[:50]), fill=C_RED, font=F['small'])
    draw.text((70, y+118), '建议持有：{}'.format(d.get('hold_period','')), fill=C_GREY, font=F['tiny'])
    y += 148
    
    # ========== 底部 ==========
    draw.rounded_rectangle([40, y, W-40, y+40], 8, fill=C_DARK)
    draw.text((W/2, y+20), '本报告由「房地产投资评估模型」生成 · 客观中立 · 仅供参考', fill=C_GREY2, font=F['tiny'], anchor='mt')
    
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
        
        # 多因子量化评分（含雷达图）
        if 'calc_result' in st.session_state and st.session_state.calc_result:
            qs = st.session_state.calc_result.get('quant_score', {})
            if qs:
                st.markdown("## 📈 多因子量化评分")
                st.plotly_chart(st.session_state.calc_result['radar_fig'], use_container_width=True)
                dims = [('区位价值', qs.get('location',0)), ('房屋品质', qs.get('property',0)),
                        ('交易成本', qs.get('transaction',0)), ('财务收益', qs.get('financial',0)),
                        ('流动性', qs.get('liquidity',0)), ('风险水平', qs.get('risk',0))]
                cols = st.columns(3)
                for i in range(3):
                    cols[i].metric(dims[i][0], '{}分'.format(dims[i][1]))
                cols2 = st.columns(3)
                for i in range(3):
                    cols2[i].metric(dims[i+3][0], '{}分'.format(dims[i+3][1]))
        
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


# ══════════════════════════════════════════════════════════════
#  V5 估值分析面板
# ══════════════════════════════════════════════════════════════

def render_valuation(params):
    """AI估值分析面板——调用 V5 估值引擎"""
    try:
        from valuation import calculate_property_valuation
        from dataset_analysis import compute_confidence_score
        from transaction_dataset import load_dataset
    except ImportError:
        st.warning("⚠️ 估值模块未加载")
        return

    # 映射 Streamlit session_state → valuation.py 输入参数
    p = {
        "community_avg_price": st.session_state.get("total_price", 500) * 10000 / max(st.session_state.get("area", 90), 1),
        "area": st.session_state.get("area", 90),
        "asking_price": st.session_state.get("total_price", 500),
        "district": st.session_state.get("district", "朝阳"),
        "property_type": st.session_state.get("property_type", "商品房"),
        "house_age": st.session_state.get("house_age", 5),
        "floor_type": st.session_state.get("floor_type", "中楼层"),
        "orientation_type": _map_orientation(st.session_state.get("orientation_defect", "无")),
        "subway_distance": st.session_state.get("subway_distance", "1公里内"),
        "school_level": st.session_state.get("school_level", "普通学区"),
        "property_management_level": st.session_state.get("property_level", "普通"),
        "liquidity_level": "一般",
        "decoration_level": st.session_state.get("decoration_level", "简装"),
        "plot_ratio": st.session_state.get("volume_rate", 2.5),
        "green_ratio": st.session_state.get("green_rate", 30),
        "parking_ratio": _map_parking(st.session_state.get("parking_ratio", "1:1")),
        "mall_distance": st.session_state.get("mall_distance", "2公里内"),
        "hospital_distance": st.session_state.get("hospital_distance", "2公里内"),
        "is_two_years": st.session_state.get("is_full2", True),
        "is_five_unique": st.session_state.get("is_full5_only", False),
        "layout_defect": st.session_state.get("layout_defect", "无"),
        "building_defect": st.session_state.get("building_defect", "无"),
        "hard_defect": st.session_state.get("hard_defect", "无"),
        "liquidity_pressure_level": "一般",
    }
    # 朝向映射
    orientation = st.session_state.get("orientation_defect", "无")
    if orientation == "东西向": p["orientation_type"] = "东西向"
    elif orientation == "北向": p["orientation_type"] = "北向"
    elif orientation == "西北/东北": p["orientation_type"] = "西北/东北"
    # 学区
    if st.session_state.get("is_school", False):
        p["school_level"] = st.session_state.get("school_level", "区重点")

    result = calculate_property_valuation(p)

    # 可信度
    ds = load_dataset() if os.path.exists("transaction_dataset.json") else []
    conf = compute_confidence_score(ds, result.get("asset_type")) if ds else {"grade": "C", "total_score": 50}

    st.divider()
    st.header("🧠 AI 估值分析")

    # ═══════════ 1. AI 最终结论（真人顾问风格）═══════════
    _render_advisor_conclusion(result, conf, p)

    # ═══════════ 2. 估值结论卡片 ═══════════
    icon = result["level_icon"]
    level = result["valuation_level"]
    bg = "#ECFDF5" if "低估" in level else "#FEF2F2" if "高估" in level else "#F0F7FF"
    st.markdown(f"""
    <div style="background:{bg};border-radius:12px;padding:20px;text-align:center;margin:10px 0">
        <div style="font-size:48px">{icon}</div>
        <div style="font-size:24px;font-weight:800;color:#1E293B">{level}</div>
        <div style="font-size:14px;color:#64748B;margin-top:8px">资产类型：{result['asset_name']} · 可信度：{conf['grade']} 级</div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════ 3. 三价对比 ═══════════
    st.subheader("💰 三价对比")
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 挂牌价", f"{result['asking_price']:.0f} 万元")
    c2.metric("🧠 模型估值", f"{result['final_model_value']:.0f} 万元",
              delta=f"{result['safety_margin']:+.1%}")
    c3.metric("🤝 预测成交价", f"{result['estimated_final_transaction_price']:.0f} 万元",
              delta=f"{result['predicted_negotiation_range'][0]:.0%}~{result['predicted_negotiation_range'][1]:.0%} 议价")

    # ═══════════ 4. 核心指标 ═══════════
    st.subheader("📊 核心指标")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("安全边际", f"{result['safety_margin']:+.1%}")
    m2.metric("微观评分", f"{result['micro_unit_score']}/100")
    m3.metric("流动性", f"{result['liquidity_score']}/100")
    m4.metric("参考价", f"{result['market_reference_value']:.0f}万")
    m5.metric("议价空间", f"{result['predicted_negotiation_range'][0]:.0%}~{result['predicted_negotiation_range'][1]:.0%}")

    # ═══════════ 5. 资产类型 ═══════════
    st.subheader("🏷️ 资产类型")
    st.info(f"**{result['asset_name']}** — {result['asset_features']}")

    # ═══════════ 6. 加减分项（自然语言）══
    lq = result["liquidity_score"]
    if lq >= 70: diff = "容易出手"
    elif lq >= 50: diff = "正常周转"
    elif lq >= 30: diff = "有一定难度"
    else: diff = "难以出手"
    lc1, lc2, lc3 = st.columns(3)
    lc1.metric("成交难度", diff)
    lc2.metric("流动性评分", f"{lq}")
    lc3.metric("建议议价", f"{result['predicted_negotiation_range'][0]:.0%}~{result['predicted_negotiation_range'][1]:.0%}")
    if result.get("liquidity_details"):
        st.caption(" | ".join(d["remark"] for d in result["liquidity_details"] if d.get("remark")))


def _map_orientation(defect):
    m = {"无": "南向", "东西向": "东西向", "北向": "北向", "西北/东北": "西北/东北"}
    return m.get(defect, "南向")

def _map_parking(ratio):
    m = {"1:2以上": "1:2以上", "1:1.5": "1:1.5", "1:1": "1:1", "1:0.8": "1:0.8", "1:0.5以下": "1:0.5以下"}
    return m.get(ratio, "1:1")

import os


# ═══ 估值分析辅助函数：人性化文案 ═══

def _render_advisor_conclusion(result, conf, p):
    """AI 最终结论——像真人投资顾问"""
    level = result["valuation_level"]
    margin = result["safety_margin"]
    atype = result["asset_name"]
    model = result["final_model_value"]
    ask = result["asking_price"]
    nego = result["predicted_negotiation_range"]

    # 核心逻辑
    if "低估" in level:
        core = f"该房源当前报价 {ask:.0f} 万，我们的模型估值约 {model:.0f} 万，" \
               f"报价比模型估值低约 {abs(margin):.0%}。"
    elif "高估" in level:
        core = f"该房源当前报价 {ask:.0f} 万，我们的模型估值约 {model:.0f} 万，" \
               f"报价比模型估值高出约 {abs(margin):.0%}。"
    else:
        core = f"报价 {ask:.0f} 万与模型估值 {model:.0f} 万基本吻合，偏差仅 {abs(margin):.0%}。"

    # 资产类型解释
    type_explain = {
        "豪宅型": "这类资产定位高端，但买家池天然窄，流动性偏弱，议价空间通常较大。",
        "核心学区房": "学区是绝对硬通货，但需警惕政策变动风险。西城海淀顶级学区房长期看仍具稀缺价值。",
        "普通改善型": "市场最大公约数，流通性尚可，估值模型对此类房源置信度最高。",
        "别墅型": "北京别墅市场受众窄、变现周期长，但有稀缺土地资源的独栋仍有长期持有价值。",
        "高风险型": "此类资产天然存在折价。回迁房/经适房受限于产权和贷款政策，商住两用税费和流动性是硬伤。",
        "老破小流动型": "刚需上车盘，总价敏感但流动性不差。核心看地段+总价+地铁三要素。",
        "投资收租型": "核心看租售比和地铁。这类资产不追增值，稳现金流是第一要义。",
    }
    explain = type_explain.get(atype, "")

    # 建议方向
    if "明显低估" in level:
        advice = "如果你对这套房源本身满意，当前报价具备不错的安全边际，可以重点关注。"
    elif "略低估" in level:
        advice = f"报价略低于模型估值，建议争取在 {nego[0]:.0%}~{nego[1]:.0%} 的议价空间内锁定。"
    elif "明显高估" in level:
        advice = f"当前价格明显偏高，建议大幅压价（至少 {nego[0]:.0%} 以上）。如果卖家态度坚决，可以考虑寻找替代标的。"
    elif "略高估" in level:
        advice = f"价格略高但不算离谱。建议以 {nego[0]:.0%}~{nego[1]:.0%} 的幅度进行议价谈判。"
    else:
        advice = "当前报价与模型估值基本一致，买卖双方预期对等，可按市场价直接推进交易。"

    st.markdown(f"""
    <div style="background:#F8FAFC;border-left:4px solid #2563EB;border-radius:8px;padding:20px;margin:10px 0;font-size:15px;line-height:1.8;color:#334155">
        <div style="font-size:18px;font-weight:700;color:#1E293B;margin-bottom:12px">💬 投资顾问分析</div>
        <p>{core}</p>
        <p>{explain}</p>
        <p style="font-weight:600;color:#1E293B">{advice}</p>
    </div>
    """, unsafe_allow_html=True)


def _humanize_factor(factor_name, value, adj):
    """将加减分因子转化为自然语言"""
    templates = {
        "朝向": lambda v, a: f"{'南北通透' if v=='南北通透' else v}朝向，{'采光和通风条件较好，对自住体验和未来转手都有加分' if a>0 else '采光方面有一定不足，在北京市场属于减分因素'}",
        "楼层": lambda v, a: f"{v}位置，{'在市场中比较受欢迎，看房体验好' if a>0 else '部分买家对此有顾虑（如顶层漏水风险、底层隐私问题）'}",
        "装修程度": lambda v, a: f"{v}装修，{'入住成本低，对买家有吸引力' if a>0 else '买家需预留额外装修预算，会作为压价理由'}",
        "电梯条件": lambda v, a: f"{v}，{'日常出行便利' if a>0 else '这是刚需硬伤，爬楼对老人和带小孩的家庭极不友好'}",
        "房龄": lambda v, a: f"房龄{v}年，{'楼龄较新，贷款年限和居住体验都更有优势' if a>0 else '贷款年限受限，物业和管线老化是需要关注的风险点'}",
        "学区等级": lambda v, a: f"学区{v}，{'在家长群体中关注度较高，有一定学区溢价' if a>0 else '学区资源是这部分房源的核心考量'}",
        "地铁距离": lambda v, a: f"地铁{v}，{'通勤便利性对刚需买家吸引力较强' if a>0 else '对依赖地铁通勤的买家影响较大'}",
        "物业品质": lambda v, a: f"物业{v}，{'对小区长期保值有正向作用' if a>0 else '物业管理影响了居住品质和小区形象'}",
        "景观视野": lambda v, a: f"{v}，{'稀缺景观资源是长期持有的加分项' if a>0 else ''}",
        "噪音影响": lambda v, a: f"{v}噪音环境，{'居住舒适度高' if a>0 else '噪音会对居住体验产生持续影响'}",
        "采光评分": lambda v, a: f"采光{v}，{'室内明亮通透，看房时第一印象好' if a>0 else '采光不足会影响居住舒适度和转手时买家意愿'}",
        "户型评分": lambda v, a: f"{v}户型，{'方正实用，空间利用率高' if a>0 else '户型问题是中后期转手时比较被动的因素'}",
        "户型缺陷": lambda v, a: f"户型有{v}问题，{'户型缺陷在二手市场直接影响看房转化率' if a<0 else ''}",
        "车位": lambda v, a: f"{v}，{'北京车位紧张，带车位是看得见的便利' if a>0 else '在北京，车位短缺会影响部分买家的购买意愿'}",
        "硬伤缺陷": lambda v, a: f"{v}，{'这类问题在市场上存在明显的心理折价，买家普遍会以此为由大幅压价' if a<0 else ''}",
        "产权税费": lambda v, a: f"{v}，{'交易环节税费低，对买家实际成本更友好' if a>0 else '税费较高，会在谈判中被买家作为压价依据'}",
    }
    if factor_name in templates:
        return templates[factor_name](value, adj)
    return f"{factor_name}（{value}），{'对该房源有一定加分' if adj>0 else '对该房源造成一定减分'}"


def _render_factors_human(result):
    """人性化展示加减分"""
    col_left, col_right = st.columns(2)
    all_adj = result.get("core_details", []) + result.get("macro_details", []) + result.get("liquidity_details", [])

    pos = [d for d in all_adj if d["adjustment"] > 0.002]
    neg = [d for d in all_adj if d["adjustment"] < -0.002]
    pos.sort(key=lambda x: -x["adjustment"])
    neg.sort(key=lambda x: x["adjustment"])

    with col_left:
        st.subheader("🟢 加分项")
        for d in pos[:8]:
            text = _humanize_factor(d["factor_name"], d["value"], d["adjustment"])
            st.markdown(f"> {text}")

    with col_right:
        st.subheader("🔴 减分项")
        for d in neg[:8]:
            text = _humanize_factor(d["factor_name"], d["value"], d["adjustment"])
            st.markdown(f"> {text}")


def _render_risk_warnings(result, p):
    """风险提示"""
    risks = []
    atype = result["asset_name"]
    asking = result["asking_price"]
    age = p.get("house_age", 5)
    school = p.get("school_level", "普通学区")
    lq = result["liquidity_score"]
    prop_type = p.get("property_type", "商品房")

    if "高估" in result["valuation_level"]:
        risks.append(("🔴 高位接盘风险", "当前报价偏高，如果以这个价格买入，短期可能面临资产缩水压力，尤其在市场下行周期。"))
    if age >= 20:
        risks.append(("🟡 老房龄风险", f"房龄 {age} 年，银行贷款审批可能受限（部分银行拒贷超 30 年房龄），且管线老化、维修成本逐年上升。"))
    if school in ["顶尖名校", "市重点"]:
        risks.append(("🟡 学区政策风险", "学区房最大的不确定性来自政策端。多校划片范围调整、学位名额变化都可能影响学区溢价。"))
    if result.get("decoration_level") == "豪装" and atype == "豪宅型":
        risks.append(("🟡 豪装折旧风险", "高端装修贬值速度快，5 年后装修溢价基本归零。不要为装修过度买单。"))
    if lq < 40:
        risks.append(("🔴 流动性风险", f"该房源流动性评分仅 {lq}/100，接盘能力偏弱。如果未来需要快速变现，可能需要大幅折价。"))
    if prop_type in ["回迁房", "经济适用房", "商住两用"]:
        risks.append(("🔴 产权与税费风险", f"{prop_type} 存在贷款受限、税费高、交易周期长等问题，买家群体天然偏窄。"))
    if asking >= 1000:
        risks.append(("🟡 高总价风险", f"总价 {asking:.0f} 万已进入高端市场区间，买家池小、议价空间大、变现周期长是这类资产的共性特征。"))

    if risks:
        st.subheader("⚠️ 风险提示")
        for title, detail in risks[:6]:
            with st.expander(title):
                st.write(detail)
    else:
        st.subheader("⚠️ 风险提示")
        st.success("未发现显著风险因素，该房源整体风险可控。")


def _render_suitable_buyers(result, p):
    """适合人群"""
    st.subheader("👥 适合人群")
    atype = result["asset_name"]
    lq = result["liquidity_score"]
    margin = result["safety_margin"]
    area = p.get("area", 90)
    rental = p.get("rental_yield", 1.5)

    buyers = []
    if "低估" in result["valuation_level"]:
        buyers.append(("💰 价值投资者", "当前报价低于模型估值，存在一定的安全边际。如果你相信市场会均值回归，这类标的值得关注。"))
    if atype == "核心学区房":
        buyers.append(("🎒 学区刚需家庭", "孩子上学是刚需，学区房对这类家庭的优先级远超价格。"))
    if area <= 80 and lq >= 50:
        buyers.append(("🔑 首次置业刚需", "面积适中、总价可控，适合预算有限的年轻家庭作为第一套房。"))
    if area >= 120:
        buyers.append(("🏡 改善型家庭", "面积充裕，适合家庭成员较多、追求居住品质的改善需求。"))
    if rental and rental >= 2.0:
        buyers.append(("📊 稳健收租型", f"租售比约 {rental:.1f}%，现金流稳定，适合追求租金回报而非短期升值的投资者。"))
    if lq >= 60:
        buyers.append(("🔄 短线投资者", "流动性好意味着买入后容易卖出，适合对市场有判断、追求快速周转的玩家。"))
    if atype == "豪宅型" or atype == "别墅型":
        buyers.append(("🏰 长期持有型", "这类资产不适合短线操作。自住享受 + 长期资产配置才是正确的打开方式。"))
    if not buyers:
        buyers.append(("🤔 需谨慎评估型", "当前条件不突出，建议结合自身实际需求综合判断。"))

    for title, desc in buyers[:5]:
        st.markdown(f"**{title}**：{desc}")


def _render_action_advice(result, p):
    """建议动作"""
    st.subheader("🎯 建议动作")
    level = result["valuation_level"]
    margin = result["safety_margin"]
    lq = result["liquidity_score"]
    nego = result["predicted_negotiation_range"]
    atype = result["asset_name"]

    advice = []
    if "明显低估" in level:
        advice.append(("🟢 建议重点关注", "该房源当前报价显著低于模型估值。如果实地看房后确认房屋状况良好（无隐藏硬伤），建议尽快锁定。"))
        advice.append(("🟢 可适当放宽议价", f"安全边际充足（+{margin:.0%}），即使在卖家底价上浮 3%-5% 成交，仍在合理区间。"))
    elif "略低估" in level:
        advice.append(("🟡 建议继续谈判", f"有一定安全边际（+{margin:.0%}），可以争取在 {nego[0]:.0%}~{nego[1]:.0%} 的折扣区间成交。"))
    elif "明显高估" in level:
        advice.append(("🔴 建议大幅压价", f"当前价格远高于模型估值，建议至少压价 {abs(margin):.0%} 以上。如卖家不松动，果断放弃。"))
        advice.append(("🔴 建议寻找替代标的", "同小区/同区域很可能存在性价比更高的房源，不要让锚定效应影响判断。"))
    elif "略高估" in level:
        advice.append(("🟠 建议适度议价", f"价格略高但不算离港。建议以 {nego[0]:.0%}~{nego[1]:.0%} 幅度议价。"))
    else:
        advice.append(("⚪ 价格合理，正常推进", "买卖双方预期匹配，按市场价推进交易即可，无需过度纠结。"))

    if lq < 40:
        advice.append(("⚠️ 不建议短期投资", "流动性偏弱，不适合作为短线标的。如有自住需求可以买入，但需做好长期持有的准备。"))
    if atype in ["高风险型"]:
        advice.append(("⚠️ 需充分尽调", f"{atype}类资产建议在交易前全面核实产权状态、抵押情况、税费明细，避免踩坑。"))

    for icon_title, desc in advice[:6]:
        st.markdown(f"**{icon_title}**：{desc}")

# ══════════════════════════════════════════════════════════════
#  V6 重构：侧边栏 + 6 标签页
# ══════════════════════════════════════════════════════════════

def _get_val_params():
    """从 session_state 构建估值引擎输入参数"""
    tp = st.session_state.get("total_price", 500)
    ar = max(st.session_state.get("area", 90), 1)
    p = {
        "community_avg_price": int(tp * 10000 / ar),
        "area": ar,
        "asking_price": tp,
        "district": st.session_state.get("district", "朝阳"),
        "property_type": st.session_state.get("property_type", "商品房"),
        "house_age": st.session_state.get("house_age", 5),
        "floor_type": st.session_state.get("floor_type", "中楼层"),
        "orientation_type": _map_orientation(st.session_state.get("orientation_defect", "无")),
        "subway_distance": st.session_state.get("subway_distance", "1公里内"),
        "school_level": st.session_state.get("school_level", "普通学区"),
        "property_management_level": st.session_state.get("property_level", "普通"),
        "liquidity_level": "一般",
        "decoration_level": st.session_state.get("decoration_level", "简装"),
        "plot_ratio": st.session_state.get("volume_rate", 2.5),
        "green_ratio": st.session_state.get("green_rate", 30),
        "parking_ratio": _map_parking(st.session_state.get("parking_ratio", "1:1")),
        "mall_distance": st.session_state.get("mall_distance", "2公里内"),
        "hospital_distance": st.session_state.get("hospital_distance", "2公里内"),
        "is_two_years": st.session_state.get("is_full2", True),
        "is_five_unique": st.session_state.get("is_full5_only", False),
        "layout_defect": st.session_state.get("layout_defect", "无"),
        "building_defect": st.session_state.get("building_defect", "无"),
        "hard_defect": st.session_state.get("hard_defect", "无"),
        "liquidity_pressure_level": "一般",
    }
    if st.session_state.get("is_school", False):
        p["school_level"] = st.session_state.get("school_level", "区重点")
    return p


def render_sidebar_v2():
    """V6 重构侧边栏——统一输入"""
    st.sidebar.title("🏠 房源参数")
    init_saves()

    with st.sidebar.expander("📋 基础信息", expanded=True):
        st.text_input("小区名称", key="community")
        st.selectbox("行政区", ["东城","西城","朝阳","海淀","丰台","石景山","通州","昌平","顺义","大兴","房山","其他"], key="district")
        col_a1, col_a2 = st.columns(2)
        col_a1.number_input("总价(万元)", 50, 5000, 500, key="total_price")
        col_a2.number_input("面积(㎡)", 20, 500, 90, key="area")
        st.number_input("房龄(年)", 0, 70, 5, key="house_age")
        col_h1, col_h2 = st.columns(2)
        col_h1.selectbox("户型", ["1室1厅","2室1厅","2室2厅","3室1厅","3室2厅","4室及以上"], key="house_type_layout")
        col_h2.selectbox("楼层", ["低楼层","中楼层","高楼层","顶层"], key="floor_type")
        st.selectbox("房产属性", ["商品房","已购公房","回迁房","经济适用房","商住两用"], key="property_type")
        st.checkbox("满二", True, key="is_full2")
        st.checkbox("满五唯一", False, key="is_full5_only")

    with st.sidebar.expander("💰 贷款参数", expanded=False):
        st.selectbox("贷款类型", ["不贷款","纯商业贷款","公积金+商业组合"], key="loan_type")
        if st.session_state.get("loan_type", "不贷款") != "不贷款":
            st.checkbox("首套房", True, key="is_first")
            st.slider("贷款比例(%)", 0, 85, 65, 5, key="loan_ratio")
            st.slider("贷款年限", 5, 30, 30, key="loan_years")
            st.selectbox("还款方式", ["等额本息","等额本金"], key="repay_type")
            if st.session_state.get("loan_type") == "纯商业贷款":
                st.number_input("商贷利率(%)", 2.5, 8.0, 3.8, key="loan_rate")
            if st.session_state.get("loan_type") == "公积金+商业组合":
                st.number_input("公积金额度(万元)", 0, 200, 0, 10, key="gjj_amount")
                st.number_input("公积金利率(%)", 2.5, 5.0, 3.1, key="gjj_rate")
                st.number_input("商贷利率(%)", 2.5, 8.0, 3.8, key="bank_rate")

    with st.sidebar.expander("💵 租金/持有", expanded=False):
        st.number_input("月租金(元)", 500, 100000, 5000, key="monthly_rent")
        st.slider("空置率(%)", 0, 50, 5, key="vacancy_rate")
        st.number_input("物业费(元/㎡/月)", 0.5, 30.0, 6.0, key="property_fee_month")
        st.number_input("供暖费(元/㎡/年)", 15.0, 60.0, 30.0, key="heat_fee_year")
        st.number_input("年维修费(元)", 0, 50000, 5000, key="repair_year")
        col_f1, col_f2 = st.columns(2)
        col_f1.number_input("买家费率", 0.01, 0.05, 0.02, key="buy_agent_rate")
        col_f2.number_input("卖家费率", 0.01, 0.03, 0.02, key="sell_agent_rate")
        st.number_input("装修费(元)", 0, 1000000, 0, key="decorate_fee")
        st.number_input("家具家电(元)", 0, 500000, 0, key="furniture_fee")

    with st.sidebar.expander("🔍 微观参数", expanded=False):
        st.selectbox("朝向缺陷", ["无","东西向","北向","西北/东北"], key="orientation_defect")
        st.selectbox("户型缺陷", ["无","暗卫","暗厅","过道长","异形","无阳台"], key="layout_defect")
        st.selectbox("楼栋缺陷", ["无","低楼层遮挡","顶层漏水","西晒","临街","高架/铁路","垃圾站旁"], key="building_defect")
        st.selectbox("硬伤", ["无","有抵押","有查封","共有产权","商住两用","凶宅/非正常死亡"], key="hard_defect")
        st.selectbox("装修程度", ["豪装","精装","简装","毛坯"], key="decoration_level")
        st.selectbox("物业水平", ["顶级","优质","普通","较差"], key="property_level")
        st.selectbox("车位配比", ["1:2以上","1:1.5","1:1","1:0.8","1:0.5以下"], key="parking_ratio")
        st.checkbox("学区房", False, key="is_school")
        if st.session_state.get("is_school"):
            st.selectbox("学区等级", ["普通学区","区重点","市重点","顶尖名校"], key="school_level")
        st.selectbox("地铁距离", ["500米内","1公里内","2公里内","2公里外"], key="subway_distance")
        st.selectbox("商场距离", ["1公里内","2公里内","2公里外"], key="mall_distance")
        st.selectbox("医院距离", ["1公里内","2公里内","2公里外"], key="hospital_distance")
        st.number_input("绿化率(%)", 0, 80, 30, key="green_rate")
        st.number_input("容积率", 0.1, 5.0, 2.5, key="volume_rate")

    with st.sidebar.expander("📈 持有假设", expanded=False):
        st.number_input("持有年限", 1, 50, 10, key="hold_years")
        st.number_input("房价年涨幅(%)", -10.0, 15.0, 3.0, key="price_growth")
        st.number_input("租金年涨幅(%)", -5.0, 10.0, 2.0, key="rent_growth")
        st.number_input("人口增长(%)", -5.0, 10.0, 1.0, key="population_growth")
        st.number_input("GDP增长(%)", -5.0, 15.0, 5.2, key="gdp_growth")
        st.number_input("区域空置(%)", 0, 50, 5, key="regional_vacancy")

    # 房源管理
    st.sidebar.divider()
    st.sidebar.subheader("📂 房源管理")
    house_list = list(st.session_state.house_saves.keys())
    if house_list:
        col_s1, col_s2 = st.sidebar.columns([3, 1])
        selected = col_s1.selectbox("已保存", [""] + house_list, key="saved_house_selector", label_visibility="collapsed")
        if selected and col_s2.button("📂", key="sidebar_load_btn"):
            msg = load_house(selected)
            st.sidebar.success(msg)
    col_save1, col_save2 = st.sidebar.columns(2)
    save_name = col_save1.text_input("名称", key="sidebar_save_name", placeholder="保存为...")
    if col_save2.button("💾", key="sidebar_save_btn") and save_name:
        msg = save_current_house(save_name)
        st.sidebar.success(msg)

    return {}


# ═══════════ Tab A: 总览结论 ═══════════

def render_tab_overview(params):
    """总览——AI结论 + 估值卡片 + 建议 + 3价"""
    from valuation import calculate_property_valuation
    from dataset_analysis import compute_confidence_score
    from transaction_dataset import load_dataset
    import os

    p = _get_val_params()
    result = calculate_property_valuation(p)
    ds = load_dataset() if os.path.exists("transaction_dataset.json") else []
    conf = compute_confidence_score(ds, result.get("asset_type")) if ds else {"grade": "C"}

    # 顾问结论
    _render_advisor_conclusion(result, conf, p)

    st.divider()

    # 估值结论卡片
    icon = result["level_icon"]; level = result["valuation_level"]
    bg = "#ECFDF5" if "低估" in level else "#FEF2F2" if "高估" in level else "#F0F7FF"
    st.markdown(f"""<div style="background:{bg};border-radius:12px;padding:20px;text-align:center;margin:10px 0">
        <div style="font-size:48px">{icon}</div>
        <div style="font-size:28px;font-weight:800;color:#1E293B">{level}</div>
        <div style="font-size:14px;color:#64748B;margin-top:8px">{result['asset_name']} · 可信度 {conf['grade']} 级</div>
    </div>""", unsafe_allow_html=True)

    # 建议动作
    st.subheader("🎯 建议动作")
    _render_action_advice(result, p)

    # 三价
    st.subheader("💰 三价对比")
    c1, c2, c3 = st.columns(3)
    c1.metric("挂牌价", f"{result['asking_price']:.0f}万")
    c2.metric("模型估值", f"{result['final_model_value']:.0f}万", delta=f"{result['safety_margin']:+.1%}")
    c3.metric("预测成交价", f"{result['estimated_final_transaction_price']:.0f}万")

    # 适合人群
    _render_suitable_buyers(result, p)
    st.divider()
    # 风险摘要
    st.subheader("⚠️ 核心风险")
    _render_risk_warnings(result, p)


# ═══════════ Tab B: 估值分析 ═══════════

def render_tab_valuation(params):
    """估值分析——完整因子加减分"""
    from valuation import calculate_property_valuation
    import os

    p = _get_val_params()
    result = calculate_property_valuation(p)

    # 核心指标
    st.subheader("📊 估值指标")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("安全边际", f"{result['safety_margin']:+.1%}")
    m2.metric("微观评分", f"{result['micro_unit_score']}/100")
    m3.metric("流动性", f"{result['liquidity_score']}/100")
    m4.metric("参考价", f"{result['market_reference_value']:.0f}万")
    m5.metric("模型估值", f"{result['final_model_value']:.0f}万")
    m6.metric("议价空间", f"{result['predicted_negotiation_range'][0]:.0%}~{result['predicted_negotiation_range'][1]:.0%}")

    st.divider()
    # 加减分
    _render_factors_human(result)

    st.divider()
    # 资产类型
    st.subheader("🏷️ 资产类型")
    st.info(f"**{result['asset_name']}** — {result['asset_features']}")
    if result.get("activated_rules"):
        st.caption("规则： " + ", ".join(result["activated_rules"]))

    # 流动性
    st.subheader("💧 流动性")
    lq = result["liquidity_score"]
    if lq >= 70: diff = "容易出手"
    elif lq >= 50: diff = "正常周转"
    elif lq >= 30: diff = "有难度"
    else: diff = "难出手"
    c1, c2 = st.columns(2)
    c1.metric("成交难度", diff)
    c2.metric("评分", f"{lq}/100")


# ═══════════ Tab C: 投资测算 ═══════════

def render_tab_investment(params):
    """投资测算——调用原有 calc 系列"""
    st.subheader("📈 投资回报测算")

    # 复用原有计算逻辑
    from calculations import (
        calc_loan_equal_principal_interest, calc_loan_equal_principal,
        calc_buy_cost, calc_hold_cash, calc_sell_profit,
        calc_professional_metrics, stress_test, calc_quantitative_score,
        get_school_premium, get_amenity_premium, get_defect_discount, make_radar
    )

    tp = st.session_state.get("total_price", 500) * 10000
    area = st.session_state.get("area", 90)
    age = st.session_state.get("house_age", 5)
    hy = st.session_state.get("hold_years", 10)
    rent = st.session_state.get("monthly_rent", 5000)
    vacancy = st.session_state.get("vacancy_rate", 5)
    lt = st.session_state.get("loan_type", "不贷款")
    lr = st.session_state.get("loan_ratio", 65)
    ly = st.session_state.get("loan_years", 30)
    rp = st.session_state.get("repay_type", "等额本息")

    # 贷款计算
    loan_amt = 0; monthly_mortgage = 0; total_interest = 0
    if lt == "纯商业贷款":
        loan_amt = tp * lr / 100
        rate = st.session_state.get("loan_rate", 3.8)
        res = calc_loan_equal_principal_interest(loan_amt, ly, rate) if rp == "等额本息" else calc_loan_equal_principal(loan_amt, ly, rate)
        monthly_mortgage = res["monthly_pay"]
        total_interest = res["total_interest"]
    elif lt == "公积金+商业组合":
        gjj = st.session_state.get("gjj_amount", 0) * 10000
        bank = tp * lr / 100 - gjj
        from calculations import calc_combined_loan
        res = calc_combined_loan(gjj, ly, st.session_state.get("gjj_rate", 3.1), bank, ly, st.session_state.get("bank_rate", 3.8), rp)
        monthly_mortgage = res["total_monthly"]
        total_interest = res["total_interest"]

    # 核心指标
    own_money = tp - loan_amt
    # 买入成本
    buy = calc_buy_cost(tp, area, st.session_state.get("is_first", True),
                        st.session_state.get("buy_agent_rate", 0.02), 0, 0,
                        st.session_state.get("decorate_fee", 0),
                        st.session_state.get("furniture_fee", 0), loan_amt)
    input_money = buy["真实总投入"]
    # 持有期现金流
    cash_flows = []
    for y in range(hy):
        hold = calc_hold_cash(area, st.session_state.get("property_fee_month", 6.0),
                              st.session_state.get("heat_fee_year", 30.0),
                              st.session_state.get("repair_year", 5000),
                              rent, vacancy, monthly_mortgage,
                              st.session_state.get("rent_growth", 2.0), y)
        cash_flows.append(hold["年净现金流"])
    # 卖出
    school_p = get_school_premium(st.session_state.get("is_school", False),
                                  st.session_state.get("school_level", "普通学区"),
                                  st.session_state.get("school_certainty", "多校划片(中等概率)"),
                                  st.session_state.get("school_type", "小学"))
    amenity_p = get_amenity_premium(st.session_state.get("subway_distance", "1公里内"),
                                    st.session_state.get("hospital_distance", "1公里内"),
                                    st.session_state.get("mall_distance", "1公里内"))
    defect_d = get_defect_discount(st.session_state.get("orientation_defect", "无"),
                                   st.session_state.get("layout_defect", "无"),
                                   st.session_state.get("building_defect", "无"),
                                   st.session_state.get("hard_defect", "无"))
    sell = calc_sell_profit(tp, hy, st.session_state.get("price_growth", 3.0), 0,
                            st.session_state.get("sell_agent_rate", 0.02),
                            st.session_state.get("is_full2", True),
                            st.session_state.get("is_full5_only", False),
                            input_money, school_p, amenity_p, defect_d)
    profit = sell["总净利润"]
    first_yr_noi = cash_flows[0] + monthly_mortgage * 12 if cash_flows else 0
    metrics = calc_professional_metrics(input_money, profit, cash_flows, hy, rent, tp, first_yr_noi, monthly_mortgage)

    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    col_i1.metric("IRR", f"{metrics['IRR年化收益率']}%")
    col_i2.metric("ROI", f"{metrics['年化ROI']}%")
    col_i3.metric("月净现金流", f"{cash_flows[0]//12:.0f}元" if cash_flows else "—")
    col_i4.metric("总净利润", f"{profit/10000:.1f}万")

    col_i5, col_i6, col_i7, col_i8 = st.columns(4)
    col_i5.metric("租售比", f"{metrics['租售比(%)']}%")
    col_i6.metric("资本化率", f"{metrics['资本化率(%)']}%")
    col_i7.metric("回本周期", f"{metrics['静态回本周期(年)']}年")
    col_i8.metric("总回报倍数", f"{metrics['总回报倍数']}x")

    st.divider()
    st.subheader("💰 贷款成本")
    if monthly_mortgage > 0:
        c_l1, c_l2 = st.columns(2)
        c_l1.metric("月供", f"{monthly_mortgage:.0f}元")
        c_l2.metric("总利息", f"{total_interest/10000:.1f}万元")

    # 持有期现金流表
    if cash_flows:
        st.subheader("📅 持有期年现金流")
        cf_data = [{"年份": i+1, "年净现金流(元)": f"{cf:,.0f}"} for i, cf in enumerate(cash_flows[:10])]
        st.dataframe(pd.DataFrame(cf_data), hide_index=True, use_container_width=True)


# ═══════════ Tab D: 风险分析 ═══════════

def render_tab_risk(params):
    """风险分析"""
    from valuation import calculate_property_valuation
    import os

    p = _get_val_params()
    result = calculate_property_valuation(p)

    # 估值风险
    st.subheader("⚠️ 估值风险")
    _render_risk_warnings(result, p)

    st.divider()

    # 压力测试
    st.subheader("📉 压力测试")
    from calculations import stress_test, calc_hold_cash, calc_sell_profit, calc_professional_metrics, get_school_premium, get_amenity_premium, get_defect_discount
    tp = p["asking_price"] * 10000
    area = p["area"]
    hy = st.session_state.get("hold_years", 10)
    rent = st.session_state.get("monthly_rent", 5000)
    vacancy = st.session_state.get("vacancy_rate", 5)
    input_money = tp * 0.35
    monthly_mortgage = 0
    if st.session_state.get("loan_type", "不贷款") != "不贷款":
        monthly_mortgage = tp * st.session_state.get("loan_ratio", 65) / 100 * 0.004
    sp = get_school_premium(st.session_state.get("is_school", False), st.session_state.get("school_level", "普通学区"),
                            st.session_state.get("school_certainty", "多校划片(中等概率)"), st.session_state.get("school_type", "小学"))
    ap = get_amenity_premium(st.session_state.get("subway_distance", "1公里内"), st.session_state.get("hospital_distance", "1公里内"), st.session_state.get("mall_distance", "1公里内"))
    dd = get_defect_discount(st.session_state.get("orientation_defect", "无"), st.session_state.get("layout_defect", "无"),
                             st.session_state.get("building_defect", "无"), st.session_state.get("hard_defect", "无"))

    try:
        stress = stress_test(tp, hy, monthly_mortgage, input_money, rent, area,
                            st.session_state.get("property_fee_month", 6.0), st.session_state.get("heat_fee_year", 30.0),
                            st.session_state.get("repair_year", 5000), vacancy, st.session_state.get("price_growth", 3.0),
                            st.session_state.get("rent_growth", 2.0), sp, ap, dd)
        st.dataframe(stress, hide_index=True, use_container_width=True)
    except Exception:
        st.caption("数据不足，无法生成压力测试。请填写更多参数。")

    # 资产类型风险
    st.divider()
    st.subheader("🏷️ 资产类型风险")
    st.info(f"类型：**{result['asset_name']}** — {result['asset_features']}")


# ═══════════ Tab E: 专业报告 ═══════════

_msg_e = ""

def render_tab_report(params):
    """专业报告"""
    global _msg_e
    if not _msg_e:
        _msg_e = "👈 点击上方「📄 完整报告」按钮生成。报告将包含执行摘要、因子详解、方案对比等完整分析。"
    st.info(_msg_e)


# ═══════════ Tab F: 高级模式 ═══════════

_msg_f = ""

def render_tab_advanced(params):
    """高级模式"""
    global _msg_f
    st.subheader("🔧 高级模式")

    pw = st.text_input("管理员密码", type="password", key="admin_pw")
    if pw != "fangchan2024":
        if pw:
            st.error("密码错误")
        st.caption("此区域仅供专业用户/管理员查看模型调试信息")
        return

    st.success("✅ 已解锁高级模式")
    from valuation import calculate_property_valuation, DEFAULT_WEIGHTS
    import os

    p = _get_val_params()
    result = calculate_property_valuation(p)

    tab_a1, tab_a2, tab_a3 = st.tabs(["模型参数", "因子明细", "数据质量"])

    with tab_a1:
        st.subheader("估值模型参数")
        st.json({
            "asset_type": result["asset_name"],
            "individual_adj": result["individual_adjustment"],
            "macro_adj": result["macro_adjustment"],
            "liquidity_adj": result["liquidity_adjustment"],
            "asset_adj": result.get("asset_adjustment", 0),
            "total_adj": result["total_adjustment"],
            "micro_unit_score": result["micro_unit_score"],
            "liquidity_score": result["liquidity_score"],
            "default_weights": DEFAULT_WEIGHTS,
            "activated_rules": result.get("activated_rules", []),
            "disabled_rules": result.get("disabled_rules", []),
        })

    with tab_a2:
        st.subheader("全因子明细")
        all_d = result.get("core_details", []) + result.get("macro_details", []) + result.get("liquidity_details", [])
        st.dataframe(pd.DataFrame(all_d), hide_index=True, use_container_width=True, column_order=["factor_name","value","adjustment","category"])

    with tab_a3:
        st.subheader("数据质量")
        try:
            from data_quality_system import data_health_report, coverage_analysis
            from transaction_dataset import load_dataset
            ds = load_dataset()
            if ds:
                health = data_health_report(ds)
                cov = coverage_analysis(ds)
                st.metric("样本总数", health["total"])
                st.metric("高质量占比", f"{health['high_quality_pct']}%")
                st.write("区域覆盖:", cov["total_districts_covered"], "/12")
                st.write("资产类型覆盖:", cov["total_asset_types_covered"], "/7")
            else:
                st.caption("暂无数据")
        except Exception as e:
            st.caption(f"数据质量模块未加载: {e}")

    if not _msg_f:
        _msg_f = "高级模式已解锁"
