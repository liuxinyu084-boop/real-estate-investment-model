import pandas as pd
import numpy as np
from scipy.optimize import newton
import plotly.graph_objects as go  # 新增：修复go未定义错误

# ===================== 贷款计算 =====================
def calc_loan_equal_principal_interest(loan_amount, years, rate):
    months = years * 12
    monthly_rate = rate / 12 / 100
    if monthly_rate == 0 or loan_amount <= 0:
        monthly_pay = 0.0
        total_interest = 0.0
    else:
        monthly_pay = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        total_interest = monthly_pay * months - loan_amount
    detail = []
    remain = loan_amount
    for m in range(1, months+1):
        interest = remain * monthly_rate
        principal = monthly_pay - interest
        remain -= principal
        detail.append({"月份":m,"月供":round(monthly_pay,2),"本金":round(principal,2),"利息":round(interest,2),"剩余本金":max(round(remain,2),0)})
    return {"loan_amount":round(loan_amount,2),"loan_years":years,"rate":rate,"monthly_pay":round(monthly_pay,2),"total_interest":round(total_interest,2),"detail":pd.DataFrame(detail)}

def calc_loan_equal_principal(loan_amount, years, rate):
    months = years * 12
    monthly_rate = rate / 12 / 100
    monthly_principal = loan_amount / months if months>0 else 0
    total_interest = 0
    detail = []
    remain = loan_amount
    for m in range(1, months+1):
        interest = remain * monthly_rate
        total_interest += interest
        total_pay = monthly_principal + interest
        remain -= monthly_principal
        detail.append({"月份":m,"月供":round(total_pay,2),"本金":round(monthly_principal,2),"利息":round(interest,2),"剩余本金":max(round(remain,2),0)})
    return {"loan_amount":round(loan_amount,2),"loan_years":years,"rate":rate,"monthly_pay":round(monthly_principal+loan_amount*monthly_rate,2),"total_interest":round(total_interest,2),"detail":pd.DataFrame(detail)}

def calc_combined_loan(gjj_amount, gjj_years, gjj_rate, bank_amount, bank_years, bank_rate, repay_type):
    gjj_res = calc_loan_equal_principal_interest(gjj_amount, gjj_years, gjj_rate) if repay_type=="等额本息" else calc_loan_equal_principal(gjj_amount, gjj_years, gjj_rate)
    bank_res = calc_loan_equal_principal_interest(bank_amount, bank_years, bank_rate) if repay_type=="等额本息" else calc_loan_equal_principal(bank_amount, bank_years, bank_rate)
    combined_detail = []
    max_months = max(len(gjj_res["detail"]), len(bank_res["detail"]))
    for m in range(max_months):
        gjj_row = gjj_res["detail"].iloc[m] if m < len(gjj_res["detail"]) else {"月供":0,"本金":0,"利息":0,"剩余本金":0}
        bank_row = bank_res["detail"].iloc[m] if m < len(bank_res["detail"]) else {"月供":0,"本金":0,"利息":0,"剩余本金":0}
        combined_detail.append({
            "月份":m+1,"公积金月供":gjj_row["月供"],"商业月供":bank_row["月供"],"总月供":gjj_row["月供"]+bank_row["月供"],
            "公积金本金":gjj_row["本金"],"商业本金":bank_row["本金"],"总本金":gjj_row["本金"]+bank_row["本金"],
            "公积金利息":gjj_row["利息"],"商业利息":bank_row["利息"],"总利息":gjj_row["利息"]+bank_row["利息"],
            "公积金剩余本金":gjj_row["剩余本金"],"商业剩余本金":bank_row["剩余本金"],"总剩余本金":gjj_row["剩余本金"]+bank_row["剩余本金"]
        })
    return {
        "gjj_amount":round(gjj_amount,2),"bank_amount":round(bank_amount,2),"total_loan_amount":round(gjj_amount+bank_amount,2),
        "loan_years":gjj_years,"gjj_rate":gjj_rate,"bank_rate":bank_rate,
        "gjj_monthly":gjj_res["monthly_pay"],"bank_monthly":bank_res["monthly_pay"],"total_monthly":gjj_res["monthly_pay"]+bank_res["monthly_pay"],
        "gjj_total_interest":gjj_res["total_interest"],"bank_total_interest":bank_res["total_interest"],"total_interest":gjj_res["total_interest"]+bank_res["total_interest"],
        "detail":pd.DataFrame(combined_detail),"gjj_detail":gjj_res["detail"],"bank_detail":bank_res["detail"]
    }

# ===================== 成本与现金流计算 =====================
def calc_buy_cost(price, area, is_first, buy_agent_rate, loan_service_fee, eval_fee, decorate_fee, furniture_fee, loan_amount):
    loan_amount = min(loan_amount, price)
    deed = price * 0.01 if (is_first and area <=90) else (price * 0.015 if is_first else price * 0.03)
    agent = price * buy_agent_rate
    down = price - loan_amount
    loan_fee = loan_service_fee + eval_fee if loan_amount>0 else 0
    total_input = down + deed + agent + loan_fee + decorate_fee + furniture_fee
    return {
        "房屋总价":price,"首付金额":round(down,2),"贷款金额":round(loan_amount,2),
        "契税":round(deed,2),"买房中介费":round(agent,2),"贷款服务费":loan_service_fee,
        "评估费":eval_fee,"装修费":decorate_fee,"家具家电费":furniture_fee,"真实总投入":round(total_input,2)
    }

def calc_hold_cash(area, property_fee_month, heat_fee_year, repair_year, base_rent, vacancy_rate, monthly_mortgage, rent_growth, year):
    year_property = property_fee_month * area * 12
    year_heat = heat_fee_year * area
    year_repair = repair_year
    current_rent = base_rent * ((1 + rent_growth/100)**year)
    year_gross = current_rent * 12
    year_real = year_gross * (1 - vacancy_rate/100)
    year_operating_cost = year_property + year_heat + year_repair
    noi = year_real - year_operating_cost  # 净运营收入NOI
    year_cash = noi - monthly_mortgage*12
    return {
        "年物业费":round(year_property,2),"年供暖费":round(year_heat,2),"年维修费":round(year_repair,2),
        "年毛租金":round(year_gross,2),"年实际租金":round(year_real,2),"年运营成本":round(year_operating_cost,2),
        "净运营收入NOI":round(noi,2),"年净现金流":round(year_cash,2),"月净现金流":round(year_cash/12,2)
    }

# ===================== 溢价折价计算 =====================
def get_school_premium(is_school, level, certainty, s_type):
    if not is_school: return 0.0
    level_map = {"普通学区":0.15,"区重点":0.25,"市重点":0.35,"顶尖名校":0.4}
    cert_map = {"单校划片(100%确定性)":1.0,"多校划片(高概率)":0.8,"多校划片(中等概率)":0.6,"多校划片(低概率)":0.4}
    type_bonus = 1.2 if s_type=="九年一贯制" else 1.0
    return level_map[level] * cert_map[certainty] * type_bonus / 10

def get_amenity_premium(subway, hospital, mall):
    premium = 0.0
    subway_map = {"500米内":0.08,"1公里内":0.04,"2公里内":0.01,"2公里外":0.0}
    hospital_map = {"1公里内":0.03,"2公里内":0.01,"2公里外":0.0}
    mall_map = {"1公里内":0.04,"2公里内":0.02,"2公里外":0.0}
    return (subway_map[subway] + hospital_map[hospital] + mall_map[mall]) / 10

def get_defect_discount(orientation, layout, building, hard):
    discount = 0.0
    orientation_map = {"无":0.0,"东西向":0.05,"北向":0.08,"西北/东北":0.10}
    layout_map = {"无":0.0,"暗卫":0.03,"暗厅":0.05,"过道长":0.02,"异形":0.08,"无阳台":0.04}
    building_map = {"无":0.0,"低楼层遮挡":0.06,"顶层漏水":0.08,"西晒":0.03,"临街":0.05,"高架/铁路":0.10,"垃圾站旁":0.12}
    hard_map = {"无":0.0,"有抵押":0.02,"有查封":0.15,"共有产权":0.20,"商住两用":0.25,"凶宅/非正常死亡":0.40}
    return orientation_map[orientation] + layout_map[layout] + building_map[building] + hard_map[hard]

# ===================== 出售收益计算 =====================
def calc_sell_profit(price, hold_years, growth, remain_loan, sell_agent_rate, is_full2, is_full5_only, input_money, school_premium, amenity_premium, defect_discount):
    final_growth = growth + school_premium + amenity_premium - defect_discount
    future = price * ((1 + final_growth/100)**hold_years)
    sell_agent = future * sell_agent_rate
    vat = 0 if is_full2 else (future-price)*0.053
    tax = 0 if is_full5_only else min(future*0.01, (future-price)*0.2)
    total_cost = vat + tax + sell_agent
    get_cash = future - total_cost - remain_loan
    profit = get_cash - input_money
    return {
        "未来房价":round(future,2),"剩余贷款":round(remain_loan,2),"出售中介费":round(sell_agent,2),
        "增值税及附加":round(vat,2),"个人所得税":round(tax,2),"出售总成本":round(total_cost,2),
        "卖房到手":round(get_cash,2),"总净利润":round(profit,2)
    }

# ===================== 专业财务指标计算 =====================
def calc_professional_metrics(input_money, profit, cash_flows, hold_years, base_rent, house_price, noi, monthly_mortgage):
    roi = (profit / input_money / hold_years)*100 if input_money>0 else 0
    roe = (profit / input_money / hold_years)*100 if input_money>0 else 0
    rent_ratio = (base_rent*12/house_price)*100 if house_price>0 else 0
    cap_rate = (noi / house_price)*100 if house_price>0 else 0  # 资本化率
    cash_on_cash = (cash_flows[0] / input_money)*100 if input_money>0 else 0  # 现金回报率
    dscr = (noi / (monthly_mortgage*12)) if monthly_mortgage>0 else 999  # 债务覆盖率
    payback = input_money / cash_flows[0] if cash_flows[0]>0 else 999
    total_return_multiple = (profit + sum(cash_flows)) / input_money if input_money>0 else 0
    
    try:
        full_cash_flows = [-input_money] + cash_flows[:-1] + [cash_flows[-1] + profit]
        irr = newton(lambda r: sum(cf/(1+r)**t for t,cf in enumerate(full_cash_flows)), 0.05)*100
    except:
        irr = 0
        
    return {
        "IRR年化收益率":round(irr,2),"年化ROI":round(roi,2),"年化ROE":round(roe,2),
        "租售比(%)":round(rent_ratio,2),"资本化率(%)":round(cap_rate,2),
        "现金回报率(%)":round(cash_on_cash,2),"债务覆盖率(DSCR)":round(dscr,2),
        "静态回本周期(年)":round(payback,2),"总回报倍数":round(total_return_multiple,2)
    }

# ===================== 压力测试 =====================
def stress_test(price, hold_years, monthly_mortgage, input_money, base_rent, area, property_fee_month, heat_fee_year, repair_year, vacancy_rate, base_growth, rent_growth, school_premium, amenity_premium, defect_discount):
    scenes = [
        ("乐观情景", 5.0, 3.0, 0, 0),
        ("基准情景", base_growth, rent_growth, 0, 0),
        ("温和下行", 1.0, 1.0, 5, 0),
        ("深度下行", -5.0, -2.0, 10, 0),
        ("经济衰退", -15.0, -5.0, 15, 1),
        ("极端危机", -30.0, -10.0, 30, 2)
    ]
    res = []
    for name, p_growth, r_growth, vac_add, rate_add in scenes:
        g = p_growth + school_premium + amenity_premium - defect_discount
        vac = min(vacancy_rate + vac_add, 70)
        cash_flows = []
        for y in range(hold_years):
            hold = calc_hold_cash(area, property_fee_month, heat_fee_year, repair_year, base_rent, vac, monthly_mortgage, r_growth, y)
            cash_flows.append(hold["年净现金流"])
        profit = calc_sell_profit(price, hold_years, g, 0, 0.02, True, True, input_money, 0, 0, 0)["总净利润"]
        yd = calc_professional_metrics(input_money, profit, cash_flows, hold_years, base_rent, price, hold["净运营收入NOI"], monthly_mortgage)
        res.append({"场景":name,"IRR(%)":yd["IRR年化收益率"],"总净利润(万)":round(profit/10000,2)})
    return pd.DataFrame(res)

# ===================== 风险调整后收益 =====================
def calc_risk_adjusted_metrics(irr, volatility, risk_free_rate=2.8):
    sharpe = (irr - risk_free_rate) / volatility if volatility>0 else 0
    sortino = (irr - risk_free_rate) / (volatility*0.7) if volatility>0 else 0
    return {"夏普比率":round(sharpe,2),"索提诺比率":round(sortino,2)}

# ===================== 黑石级多因子量化评分系统 =====================
def calc_quantitative_score(params, financial_metrics):
    # 权重设置（黑石标准）
    weights = {
        "location": 0.30,  # 区位价值30%
        "property": 0.20,  # 房屋品质20%
        "transaction": 0.10,  # 交易成本10%
        "financial": 0.25,  # 财务收益25%
        "liquidity": 0.05,  # 流动性5%
        "risk": 0.10  # 风险水平10%
    }
    
    scores = {}
    
    # 1. 区位价值评分（30%）
    subway_score = {"500米内":10,"1公里内":7,"2公里内":3,"2公里外":1}[params["subway_distance"]]
    school_score = 0
    if params["is_school"]:
        school_score = {"普通学区":5,"区重点":7,"市重点":9,"顶尖名校":10}[params["school_level"]]
        school_score *= {"单校划片(100%确定性)":1.0,"多校划片(高概率)":0.8,"多校划片(中等概率)":0.6,"多校划片(低概率)":0.4}[params["school_cert"]]
    hospital_score = {"1公里内":8,"2公里内":5,"2公里外":2}[params["hospital_distance"]]
    mall_score = {"1公里内":8,"2公里内":5,"2公里外":2}[params["mall_distance"]]
    location_score = (subway_score*0.4 + school_score*0.3 + hospital_score*0.15 + mall_score*0.15)
    scores["location"] = round(location_score, 1)
    
    # 2. 房屋品质评分（20%）
    age_score = max(10 - params["house_age"]*0.5, 1)
    orientation_score = {"无":10,"东西向":6,"北向":4,"西北/东北":3}[params["orientation_defect"]]
    layout_score = {"无":10,"暗卫":7,"暗厅":5,"过道长":8,"异形":4,"无阳台":6}[params["layout_defect"]]
    floor_score = {"低楼层":6,"中楼层":10,"高楼层":8,"顶层":5}[params["floor_type"]]
    property_score = {"顶级":10,"优质":8,"普通":5,"较差":2}[params["property_level"]]
    property_total_score = (age_score*0.25 + orientation_score*0.2 + layout_score*0.2 + floor_score*0.15 + property_score*0.2)
    scores["property"] = round(property_total_score, 1)
    
    # 3. 交易成本评分（10%）
    cost_ratio = (params["buy_agent_rate"] + 0.015 + params["sell_agent_rate"]) * 100  # 预估总交易成本率
    transaction_score = max(10 - cost_ratio*2, 1)
    scores["transaction"] = round(transaction_score, 1)
    
    # 4. 财务收益评分（25%）
    irr_score = min(financial_metrics["IRR年化收益率"]*2, 10)
    cash_flow_score = 10 if financial_metrics["债务覆盖率(DSCR)"]>1.2 else (7 if financial_metrics["债务覆盖率(DSCR)"]>1 else 4)
    cap_rate_score = min(financial_metrics["资本化率(%)"]*2, 10)
    financial_score = (irr_score*0.5 + cash_flow_score*0.3 + cap_rate_score*0.2)
    scores["financial"] = round(financial_score, 1)
    
    # 5. 流动性评分（5%）
    liquidity_score = 8 if params["district"] in ["东城","西城","朝阳","海淀"] else (5 if params["district"] in ["丰台","石景山"] else 3)
    scores["liquidity"] = round(liquidity_score, 1)
    
    # 6. 风险水平评分（10%）
    leverage_score = max(10 - params["loan_ratio"]*0.1, 1)
    defect_score = max(10 - params["defect_score"]*2, 1)
    risk_score = (leverage_score*0.6 + defect_score*0.4)
    scores["risk"] = round(risk_score, 1)
    
    # 计算综合得分
    total_score = (
        scores["location"]*weights["location"] +
        scores["property"]*weights["property"] +
        scores["transaction"]*weights["transaction"] +
        scores["financial"]*weights["financial"] +
        scores["liquidity"]*weights["liquidity"] +
        scores["risk"]*weights["risk"]
    )
    
    # 评级
    def get_grade(v):
        if v>=8.5: return "A+"
        elif v>=7.5: return "A"
        elif v>=6.8: return "A-"
        elif v>=6.0: return "B+"
        elif v>=5.0: return "B"
        else: return "C+"
    
    scores["total"] = round(total_score, 1)
    scores["grade"] = get_grade(total_score)
    scores["weights"] = weights
    
    return scores

# ===================== 辅助函数 =====================
def get_asset_type(irr, month_cash, rent_ratio, loan_ratio, is_school):
    if is_school: return "学区稀缺型资产"
    if rent_ratio>2.2 and month_cash>0: return "现金流型资产"
    if loan_ratio>70 and irr>6: return "高杠杆博弈型资产"
    if irr>5 and month_cash<0: return "核心保值型资产"
    return "均衡稳健型资产"

def gen_ai_one_sentence(asset_type, irr, month_cash, is_school, defect_score, total_score):
    defect_tip = f"存在{defect_score}项核心缺陷，需谨慎评估" if defect_score>0 else "无明显硬伤缺陷"
    if total_score >=8.5:
        return f"综合评分{total_score}分，{asset_type}，{defect_tip}，强烈推荐买入，长期持有收益可观。"
    elif total_score >=7.5:
        return f"综合评分{total_score}分，{asset_type}，{defect_tip}，推荐买入，适合稳健配置。"
    elif total_score >=6.8:
        return f"综合评分{total_score}分，{asset_type}，{defect_tip}，可以买入，需注意控制风险。"
    elif total_score >=6.0:
        return f"综合评分{total_score}分，{asset_type}，{defect_tip}，谨慎买入，仅适合特定需求。"
    else:
        return f"综合评分{total_score}分，{asset_type}，{defect_tip}，不建议投资，风险较高。"

def calc_drop20_irr(price, hold_years, monthly_mortgage, input_money, base_rent, area, property_fee_month, heat_fee_year, repair_year, vacancy_rate, price_growth, rent_growth, school_premium, amenity_premium, defect_discount):
    df = stress_test(price, hold_years, monthly_mortgage, input_money, base_rent, area, property_fee_month, heat_fee_year, repair_year, vacancy_rate, price_growth, rent_growth, school_premium, amenity_premium, defect_discount)
    return round(df.iloc[4]["IRR(%)"],1)

def make_radar(scores):
    cat = ["区位价值","房屋品质","交易成本","财务收益","流动性","风险水平"]
    values = [scores["location"], scores["property"], scores["transaction"], scores["financial"], scores["liquidity"], scores["risk"]]
    fig = go.Figure(go.Scatterpolar(r=values, theta=cat, fill="toself", fillcolor="#1f77b4", opacity=0.6))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,10])), height=350, showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
    return fig