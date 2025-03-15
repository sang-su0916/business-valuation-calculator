import streamlit as st
import pandas as pd
import locale

# 숫자 형식화를 위한 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')
    except:
        locale.setlocale(locale.LC_ALL, '')

# 숫자 형식화 함수
def format_number(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

# CSS 스타일 추가
st.markdown("""
<style>
    .info-box {
        background-color: #f0f7fb;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
        color: #0c5460;
    }
    .result-card {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tax-amount {
        font-size: 28px;
        font-weight: bold;
        color: #333;
        margin: 10px 0;
    }
    .tax-description {
        color: #555;
        font-size: 0.9em;
        margin-top: 5px;
        padding: 5px 0;
        border-top: 1px solid #eee;
    }
    .tax-rate {
        color: #28a745;
        font-weight: bold;
    }
    .section-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #333;
    }
    .sidebar-guide {
        background-color: #e8f4f8;
        padding: 10px 15px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9em;
        border-left: 3px solid #4dabf7;
    }
    .calculation-explanation {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        font-size: 0.95em;
    }
    .summary-box {
        background-color: #e9f7ef;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# 페이지 헤더
st.title("현시점 세금 계산")

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

if not st.session_state.get('evaluated', False):
    st.warning("먼저 '비상장주식 평가' 페이지에서 평가를 진행해주세요.")
    st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>비상장주식 평가</b> 메뉴를 클릭하여 평가를 먼저 진행하세요.</div>", unsafe_allow_html=True)
else:
    stock_value = st.session_state.stock_value
    company_name = st.session_state.company_name
    owned_shares = st.session_state.owned_shares
    share_price = st.session_state.share_price
    eval_date = st.session_state.get('eval_date', None)
    
    # 세금 계산
    current_tax_details = calculate_tax_details(stock_value, owned_shares, share_price)
    
    # 평가된 주식 가치 정보 표시
    with st.expander("평가된 주식 가치", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**회사명:** {company_name}")
            st.markdown(f"**주당 평가액:** {format_number(stock_value['finalValue'])}원")
        with col2:
            st.markdown(f"**회사 총가치:** {format_number(stock_value['totalValue'])}원")
            st.markdown(f"**대표이사 보유주식 가치:** {format_number(stock_value['ownedValue'])}원")
        
        if eval_date:
            st.markdown(f"**평가 기준일:** {eval_date.strftime('%Y년 %m월 %d일')}")
    
    # 세금 계산 결과 설명 추가
    st.markdown("""
    <div class="calculation-explanation">
        <h3>세금 계산 결과 안내</h3>
        <p>비상장주식의 가치평가 결과를 바탕으로 다음 세 가지 경우에 대한 세금을 계산합니다:</p>
        <ul>
            <li><b>증여세</b>: 주식을 타인에게 증여하는 경우 적용되는 세금</li>
            <li><b>양도소득세</b>: 주식을 매각할 때 발생하는 시세차익에 대한 세금</li>
            <li><b>청산소득세</b>: 법인을 청산할 때 지분 가치에 대해 발생하는 세금 (법인세+배당소득세)</li>
        </ul>
        <p>각 세금은 현행 세법에 근거하여 계산됩니다. 실제 세금은 개인 상황, 공제 사항 등에 따라 달라질 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 세금 계산 결과
    st.subheader("세금 계산 결과")
    
    # 3개의 세금 결과 카드로 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>증여세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{format_number(current_tax_details['inheritanceTax'])}원</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-rate'>적용 세율: 40%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 타인에게 무상으로 증여할 경우 발생하는 세금입니다. 증여 받은 사람이 납부합니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>양도소득세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{format_number(current_tax_details['transferTax'])}원</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-rate'>적용 세율: 22%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>주식을 매각하여 발생한 이익(양도차익)에 대해 부과되는 세금입니다. 주식 매도자가 납부합니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>청산소득세</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tax-amount'>{format_number(current_tax_details['totalTax'])}원</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-rate'>법인세 25% + 배당세 15.4%</div>", unsafe_allow_html=True)
        st.markdown("<div class='tax-description'>법인 청산 시 발생하는 세금으로, 법인세와 잔여재산 분배에 따른 배당소득세로 구성됩니다.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
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
                format_number(stock_value["ownedValue"]),
                format_number(current_tax_details["acquisitionValue"]),
                format_number(current_tax_details["transferProfit"]),
                format_number(stock_value["ownedValue"]),
                format_number(current_tax_details["corporateTax"]),
                format_number(current_tax_details["afterTaxValue"]),
                format_number(current_tax_details["liquidationTax"])
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
    
    # 세금 비교 요약
    st.markdown("""
    <div class="summary-box">
        <h4>세금 비교 분석</h4>
        <p>위 계산 결과를 바탕으로 자산 처분 방법에 따른 세금 부담을 비교할 수 있습니다:</p>
        <ul>
            <li>증여 시 <b>40%</b>의 세율로 일시에 세금이 부과됩니다.</li>
            <li>주식 매각 시 <b>22%</b>의 세율이 적용되지만, 취득원가를 공제한 이익에만 부과됩니다.</li>
            <li>법인 청산 시 법인세와 배당소득세가 이중으로 부과되어 최대 <b>36.6%</b>의 실효세율이 적용될 수 있습니다.</li>
        </ul>
        <p>상황에 따라 가장 유리한 방법을 선택하는 것이 중요합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 참고사항
    st.info("※ 실제 세금은 개인 상황, 보유기간, 대주주 여부 등에 따라 달라질 수 있습니다.")
    
    # 버튼 행
    col1, col2 = st.columns(2)
    with col1:
        if st.button("주식가치 결과로 돌아가기", use_container_width=True):
            try:
                st.switch_page("2_주식가치_결과.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>주식가치 결과</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
    
    with col2:
        if st.button("미래 주식가치 계산하기", type="primary", use_container_width=True):
            try:
                st.switch_page("4_미래_주식가치.py")
            except:
                st.markdown("<div class='sidebar-guide'>왼쪽 사이드바에서 <b>미래 주식가치</b> 메뉴를 클릭하여 이동하세요.</div>", unsafe_allow_html=True)
