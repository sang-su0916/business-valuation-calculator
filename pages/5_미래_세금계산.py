import streamlit as st
import pandas as pd

# 숫자 형식화 함수
def format_number(num):
    return f"{int(num):,}"

# 세금 계산 함수
def calculate_tax_details(value, owned_shares, share_price):
    if not value:
        return None
    
    owned_value = value["ownedValue"]
    
    # 상속증여세 (40%)
    inheritance_tax = owned_value * 0.4
    
    # 양도소득세 (22%)
    acquisition_value = owned_shares * share_price
    transfer_profit = owned_value - acquisition_value
    transfer_tax = transfer_profit * 0.22
    
    # 청산소득세 계산
    corporate_tax = owned_value * 0.25
    after_tax_value = owned_value - corporate_tax
    liquidation_tax = after_tax_value * 0.154
    
    return {
        "inheritanceTax": inheritance_tax,
        "transferTax": transfer_tax,
        "corporateTax": corporate_tax,
        "liquidationTax": liquidation_tax,
        "acquisitionValue": acquisition_value,
        "transferProfit": transfer_profit,
        "afterTaxValue": after_tax_value,
        "totalTax": corporate_tax + liquidation_tax
    }

# 페이지 헤더
st.title("미래 세금 계산")

if not st.session_state.get('future_evaluated', False):
    st.warning("먼저 '미래 주식가치' 페이지에서 평가를 진행해주세요.")
    if st.button("미래 주식가치 페이지로 이동"):
        st.switch_page("4_미래_주식가치.py")
else:
    future_stock_value = st.session_state.future_stock_value
    company_name = st.session_state.company_name
    owned_shares = st.session_state.owned_shares
    share_price = st.session_state.share_price
    growth_rate = future_stock_value["growthRate"]
    future_years = future_stock_value["futureYears"]
    
    # 세금 계산
    future_tax_details = calculate_tax_details(future_stock_value, owned_shares, share_price)
    
    # 평가된 주식 가치 정보
    with st.expander("미래 주식 가치", expanded=True):
        st.markdown(f"**회사명:** {company_name}")
        st.markdown(f"**예측 기간:** {future_years}년")
        st.markdown(f"**적용 성장률:** 연 {growth_rate}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**미래 주당 평가액:** {format_number(future_stock_value['finalValue'])}원")
            st.markdown(f"**미래 회사 총가치:** {format_number(future_stock_value['totalValue'])}원")
        with col2:
            st.markdown(f"**미래 대표이사 보유주식 가치:** {format_number(future_stock_value['ownedValue'])}원")
    
    # 세금 계산 결과
    st.subheader("미래 세금 계산 결과")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "증여세", 
            f"{format_number(future_tax_details['inheritanceTax'])}원", 
            "적용 세율: 40%"
        )
    
    with col2:
        st.metric(
            "양도소득세", 
            f"{format_number(future_tax_details['transferTax'])}원", 
            "적용 세율: 22%"
        )
    
    with col3:
        st.metric(
            "청산소득세", 
            f"{format_number(future_tax_details['totalTax'])}원", 
            "법인세 25% + 배당세 15.4%"
        )
    
    # 계산 세부내역
    with st.expander("계산 세부내역", expanded=True):
        details_df = pd.DataFrame({
            "항목": [
                "증여세 과세표준", 
                "양도소득 취득가액", 
                "양도소득 차익", 
                "법인세 과세표준", 
                "법인세액", 
                "배당소득", 
                "배당소득세"
            ],
            "금액 (원)": [
                format_number(future_stock_value["ownedValue"]),
                format_number(future_tax_details["acquisitionValue"]),
                format_number(future_tax_details["transferProfit"]),
                format_number(future_stock_value["ownedValue"]),
                format_number(future_tax_details["corporateTax"]),
                format_number(future_tax_details["afterTaxValue"]),
                format_number(future_tax_details["liquidationTax"])
            ]
        })
        
        st.dataframe(
            details_df,
            column_config={
                "항목": st.column_config.TextColumn("항목"),
                "금액 (원)": st.column_config.TextColumn("금액 (원)", width="large"),
            },
            hide_index=True,
            use_container_width=True
        )
    
    # 참고사항
    st.info("※ 실제 세금은 개인 상황, 보유기간, 대주주 여부 등에 따라 달라질 수 있으며, 미래 세법이 변경될 수 있습니다.")
    
    # 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("미래 주식가치로 돌아가기", use_container_width=True):
            st.switch_page("4_미래_주식가치.py")
    
    with col2:
        if st.button("처음부터 다시 계산하기", type="primary", use_container_width=True):
            # 세션 상태 초기화
            st.session_state.evaluated = False
            st.session_state.future_evaluated = False
            st.session_state.stock_value = None
            st.session_state.future_stock_value = None
            st.switch_page("1_비상장주식_평가.py")
