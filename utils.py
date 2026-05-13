import json
import os
import streamlit as st

SAVE_FILE = "house_saves.json"

def init_saves():
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    if "house_saves" not in st.session_state:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            st.session_state.house_saves = json.load(f)

def save_current_house(name):
    if not name.strip():
        return "请输入房源名称"
    data = {
        "community": st.session_state.get("community", ""),
        "district": st.session_state.get("district", "朝阳"),
        "total_price": st.session_state.get("total_price", 500),
        "area": st.session_state.get("area", 90),
        "house_age": st.session_state.get("house_age", 5),
        "house_type_layout": st.session_state.get("house_type_layout", "2室1厅"),
        "floor_type": st.session_state.get("floor_type", "中楼层"),
        "property_type": st.session_state.get("property_type", "商品房"),
        "is_full2": st.session_state.get("is_full2", True),
        "is_full5_only": st.session_state.get("is_full5_only", False),
        "hold_years": st.session_state.get("hold_years", 10),
        "price_growth": st.session_state.get("price_growth", 3.0),
        "rent_growth": st.session_state.get("rent_growth", 2.0),
        "is_school": st.session_state.get("is_school", False),
        "school_level": st.session_state.get("school_level", "普通学区"),
        "school_certainty": st.session_state.get("school_certainty", "多校划片(中等概率)"),
        "school_type": st.session_state.get("school_type", "小学"),
        "monthly_rent": st.session_state.get("monthly_rent", 5000),
        "vacancy_rate": st.session_state.get("vacancy_rate", 5),
        "loan_type": st.session_state.get("loan_type", "不贷款"),
        "is_first": st.session_state.get("is_first", True),
        "loan_ratio": st.session_state.get("loan_ratio", 65),
        "loan_years": st.session_state.get("loan_years", 30),
        "repay_type": st.session_state.get("repay_type", "等额本息"),
        "loan_rate": st.session_state.get("loan_rate", 3.8),
        "gjj_amount": st.session_state.get("gjj_amount", 0),
        "gjj_rate": st.session_state.get("gjj_rate", 3.1),
        "bank_rate": st.session_state.get("bank_rate", 3.8),
        "loan_service_fee": st.session_state.get("loan_service_fee", 0),
        "eval_fee": st.session_state.get("eval_fee", 0),
        "decorate_fee": st.session_state.get("decorate_fee", 0),
        "furniture_fee": st.session_state.get("furniture_fee", 0),
        "property_fee_month": st.session_state.get("property_fee_month", 6.0),
        "heat_fee_year": st.session_state.get("heat_fee_year", 30.0),
        "repair_year": st.session_state.get("repair_year", 5000),
        "buy_agent_rate": st.session_state.get("buy_agent_rate", 0.02),
        "sell_agent_rate": st.session_state.get("sell_agent_rate", 0.02),
        "subway_distance": st.session_state.get("subway_distance", "500米内"),
        "hospital_distance": st.session_state.get("hospital_distance", "1公里内"),
        "mall_distance": st.session_state.get("mall_distance", "1公里内"),
        "orientation_defect": st.session_state.get("orientation_defect", "无"),
        "layout_defect": st.session_state.get("layout_defect", "无"),
        "building_defect": st.session_state.get("building_defect", "无"),
        "hard_defect": st.session_state.get("hard_defect", "无"),
        "property_level": st.session_state.get("property_level", "普通"),
        "parking_ratio": st.session_state.get("parking_ratio", "1:1"),
        "decoration_level": st.session_state.get("decoration_level", "简装")
    }
    st.session_state.house_saves[name.strip()] = data
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.house_saves, f, ensure_ascii=False, indent=2)
    return "保存成功"

def load_house(name):
    data = st.session_state.house_saves[name]
    for k, v in data.items():
        st.session_state[k] = v
    return "加载成功"

def delete_house(name):
    if name in st.session_state.house_saves:
        del st.session_state.house_saves[name]
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.house_saves, f, ensure_ascii=False, indent=2)
    return "删除成功"